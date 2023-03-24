import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import math
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path
from scipy.spatial import KDTree
import time



def read_coordinate_file(input_file):
    """ Opens and reads data from textfile as well as split and strip this data to make it useful.
        The data is also converted with mercator projection and stored in a Numpy-array.

    :param input_file: file to extract data from
    type input_file: str
    """
    R = 1
    x_coords = []
    y_coords = []
    with open(input_file) as txt_file:
        for line in txt_file:
            co_ord = line.strip('{}\n')
            co_ord = co_ord.split(',')
            x_coords.append(R * ((np.pi * float(co_ord[1])) / 180))
            y_coords.append(R * (np.log(np.tan((np.pi / 4) + ((np.pi * float(co_ord[0])) / 360)))))
    xy_coords= np.array([x_coords, y_coords])
    return xy_coords

def plot_points(coord_list, indices, path):
    """ Plots all cities, possible connections and the fastest route

    :param coord_list: contains the points to plot
    :param indices: contains the connections
    :param path: contains the order of cities to create the shortest path
    """

    segments = []
    shortest_line = []

    for i, (indexx, indexy) in enumerate(zip(indices[0], indices[1])):
        line = []
        x = (coord_list[0][indexx], coord_list[1][indexx])
        y = (coord_list[0][indexy], coord_list[1][indexy])
        line.append(x)
        line.append(y)
        segments.append(line)

    for i, p in enumerate(path):
        sp = (coord_list[0][p], coord_list[1][p])
        shortest_line.append(sp)

    line_segments = LineCollection(segments, edgecolors='black', linewidths=0.5)
    shortest_line_segments = LineCollection([shortest_line], edgecolors='blue', linewidths=2)
    fig = plt.figure(figsize=(9, 7))
    ax = fig.gca()
    ax.add_collection(line_segments)
    ax.add_collection(shortest_line_segments)
    ax.set_aspect('equal')
    plt.scatter(coord_list[0], coord_list[1], alpha=0.75, c='r')
    plt.show()


def construct_graph_connections(coord_list, radius):
    """ Iterates through all cities to determine which connections are possible.


    :param coord_list: contains coordinates of all cities
    :type coord_list: list, 2D numpy-array
    :param radius: allowed distance between cities to make a connection
    :type radius: float
    """

    city_1 = []
    city_2 = []
    distance = []
    coord_list_transposed = coord_list.T

    for i, (point_x, point_y) in enumerate(coord_list_transposed):
        for j, (x_ref, y_ref) in enumerate(coord_list_transposed):
            if i < j:
                dist = math.dist([point_x, point_y], [x_ref, y_ref])
                if dist <= radius:
                    city_1.append(i)
                    city_2.append(j)
                    distance.append(dist)
    indices = np.array([city_1, city_2])
    distance_array = np.array(distance)
    return indices, distance_array


def construct_fast_graph_connections(coord_list, radius):
    """ Creates a KDTree to determine which cities are within range of a certain city.

    :param coord_list: contains coordinates of all cities
    :type coord_list: list, 2D numpy-array
    :param radius: allowed distance between cities to make a connection
    :type radius: float
    """

    city1 = []
    city2 = []
    distance = []

    tree = KDTree(coord_list.T)

    for i, point in enumerate(coord_list.T):
        indx = tree.query_ball_point(coord_list[:, i], radius, workers=-1)

        for j in indx:
            if i < j:
                ref = coord_list[:, j]
                city1.append(i)
                city2.append(j)
                distance.append(math.dist(point, ref))
    indices = np.array([city1, city2])
    distance_array = np.array(distance)
    return indices, distance_array


def construct_graph(indices, distance, n):
    """ Creates a sparse matrix containing the distance between possible city connections

    :param indices: contains the connections
    :param distance: contains the distance between indices
    :param n: length of coordlist
    :return: matrix with all indices and distances
    """

    row = indices[0]
    column = indices[1]
    matrix = csr_matrix((distance, (row, column)), shape=(n, n))
    return matrix


def find_shortest_path(graph, start_node, end_node):
    """ Finds the shortest path between to cities

    :param graph: Matrix with all indices and distances
    :param start_node: The city the path should start from
    :param end_node: The city the path should end in
    :return: dist_min, sequence
    """

    dist_matrix, predecessors = shortest_path(graph, indices=start_node, directed=False, return_predecessors=True)
    dist_min = dist_matrix[end_node]
    sequence = [end_node]
    x = end_node
    while x != start_node:
        sequence.append(predecessors[x])
        x = predecessors[x]

    return dist_min, sequence[::-1]


if __name__ == '__main__':
    """
    main function that calls the other functions
    """

    city = "GermanyCities.txt"
    start_node = 31
    end_node = 2
    radius = 0.0025

    # city = "SampleCoordinates.txt"
    # start_node = 0
    # end_node = 5
    # radius = 0.08

    # city = "HungaryCities.txt"
    # start_node = 311
    # end_node = 702
    # radius = 0.005

    start_time = time.time()
    coord_list = read_coordinate_file(city)
    end_time = time.time()
    print("The function \"read_coordinate_file\" takes: ", end_time - start_time, "seconds to execute")

#    start_time = time.time()
#   indices, distance_array = construct_graph_connections(coord_list, radius)
#   end_time = time.time()
#   print("The function \"construct_graph_connections\" takes: ", end_time - start_time, "seconds to execute")

    start_time = time.time()
    indices, distance_array = construct_fast_graph_connections(coord_list, radius)
    end_time = time.time()
    print("The function \"construct_fast_graph_connections\" takes: ", end_time - start_time, "seconds to execute")

    start_time = time.time()
    graph = construct_graph(indices, distance_array, len(coord_list[0]))
    end_time = time.time()
    print("The function \"construct_graph\": ", end_time - start_time, "seconds to execute")

    start_time = time.time()
    dist_min, sequence = find_shortest_path(graph, start_node, end_node)
    end_time = time.time()
    print("The function \"find_shortest_path\" takes: ", end_time - start_time, "seconds to execute")

    start_time = time.process_time()
    plot_points(coord_list, indices, sequence)
    end_time = time.process_time()
    print("The function \"plot_points\" takes: ", end_time - start_time, "seconds to execute")

    print("The total distance is: ", dist_min )
    print("The shortest path sequence is:", sequence)


