import numpy as np
from numba import jit, prange
from sklearn.metrics import accuracy_score

__all__ = ['dtw_distance', 'KnnDTW']


@jit(nopython=True, parallel=True, nogil=True)
def dtw_distance(dataset1, dataset2):
    """
    Computes the dataset DTW distance matrix using multiprocessing.

    Args:
        dataset1: timeseries dataset of shape [N1, T1, D]
        dataset2: timeseries dataset of shape [N2, T2, D]

    Returns:
        Distance matrix of shape [N1, N2]
    """
    n1 = len(dataset1)
    n2 = len(dataset2)

    dist = np.empty((n1, n2), dtype=np.float64)

    for i in prange(n1):
        for j in prange(n2):
            dist[i][j] = _dtw_distance(dataset1[i], dataset2[j])
    return dist


@jit(nopython=True, cache=True)
def _dtw_distance(series1, series2):
    """
    Returns the DTW similarity distance between two 2-D
    timeseries numpy arrays.

    Args:
        series1, series2 : array of shape [n_timepoints, D]
            Two arrays containing n_samples of timeseries data
            whose DTW distance between each sample of A and B
            will be compared.

    Returns:
        DTW distance between A and B
    """
    l1, l2 = series1.shape[0], series2.shape[0]
    E = np.empty((l1, l2))

    # Fill First Cell
    E[0][0] = _cosine(series1[0], series2[0])

    # Fill First Column
    for i in range(1, l1):
        E[i][0] = E[i - 1][0] + _cosine(series1[i], series2[0])

    # Fill First Row
    for i in range(1, l2):
        E[0][i] = E[0][i - 1] + _cosine(series1[0], series2[i])

    for i in range(1, l1):
        for j in range(1, l2):
            cost = _cosine(series1[i], series2[j])
            E[i][j] = cost + min(E[i - 1][j], E[i][j - 1], E[i - 1][j - 1])

    return E[-1][-1]

@jit(nopython=True, cache=True)
def _cosine(a, b):
    """
    Compute cosine similarity between two vectors.

    Args:
        a, b: 1-D arrays containing elements of vectors.

    Returns:
        Cosine similarity between vectors a and b.
    """
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return 1.0 - (dot_product / (norm_a * norm_b + 1e-8))  # Adding a small value to avoid division by zero

# Modified from https://github.com/markdregan/K-Nearest-Neighbors-with-Dynamic-Time-Warping
class KnnDTW(object):
    """K-nearest neighbor classifier using dynamic time warping
    as the distance measure between pairs of time series arrays

    Arguments
    ---------
    n_neighbors : int, optional (default = 1)
        Number of neighbors to use by default for KNN
    """

    def __init__(self, n_neighbors=1):
        self.n_neighbors = n_neighbors

    def fit(self, x, y):
        """Fit the model using x as training data and y as class labels

        Arguments
        ---------
        x : array of shape [n_samples, n_timepoints]
            Training data set for input into KNN classifer

        y : array of shape [n_samples]
            Training labels for input into KNN classifier
        """

        self.x = np.copy(x)
        self.y = np.copy(y)

    def _dist_matrix(self, x, y):
        """Computes the M x N distance matrix between the training
        dataset and testing dataset (y) using the DTW distance measure

        Arguments
        ---------
        x : array of shape [n_samples, n_timepoints]

        y : array of shape [n_samples, n_timepoints]

        Returns
        -------
        Distance matrix between each item of x and y with
            shape [training_n_samples, testing_n_samples]
        """
        dm = dtw_distance(x, y)

        return dm

    def predict(self, x):
        """Predict the class labels or probability estimates for
        the provided data

        Arguments
        ---------
          x : array of shape [n_samples, n_timepoints]
              Array containing the testing data set to be classified

        Returns
        -------
          2 arrays representing:
              (1) the predicted class labels
              (2) the knn label count probability
        """
        np.random.seed(0)
        dm = self._dist_matrix(x, self.x)

        # Identify the k nearest neighbors
        knn_idx = dm.argsort()[:, :self.n_neighbors]

        # Identify k nearest labels
        knn_labels = self.y[knn_idx]

        # Model Label
        mode_data = mode(knn_labels, axis=1)
        mode_label = mode_data[0]
        mode_proba = mode_data[1] / self.n_neighbors

        return mode_label.ravel(), mode_proba.ravel()

    def evaluate(self, x, y):
        """
        Predict the class labels or probability estimates for
        the provided data and then evaluates the accuracy score.

        Arguments
        ---------
          x : array of shape [n_samples, n_timepoints]
              Array containing the testing data set to be classified

          y : array of shape [n_samples]
              Array containing the labels of the testing dataset to be classified

        Returns
        -------
          1 floating point value representing the accuracy of the classifier
        """
        # Predict the labels and the probabilities
        pred_labels, pred_probas = self.predict(x)

        # Ensure labels are integers
        y = y.astype('int32')
        pred_labels = pred_labels.astype('int32')

        # Compute accuracy measure
        accuracy = accuracy_score(y, pred_labels)
        return accuracy

    def predict_proba(self, x):
        """Predict the class labels probability estimates for
        the provided data

        Arguments
        ---------
            x : array of shape [n_samples, n_timepoints]
                Array containing the testing data set to be classified

        Returns
        -------
            2 arrays representing:
                (1) the predicted class probabilities
                (2) the knn labels
        """
        np.random.seed(0)
        dm = self._dist_matrix(x, self.x)

        # Invert the distance matrix
        dm = -dm

        classes = np.unique(self.y)
        class_dm = []

        # Partition distance matrix by class
        for i, cls in enumerate(classes):
            idx = np.argwhere(self.y == cls)[:, 0]
            cls_dm = dm[:, idx]  # [N_test, N_train_c]

            # Take maximum distance vector due to softmax probabilities
            cls_dm = np.max(cls_dm, axis=-1)  # [N_test,]

            class_dm.append([cls_dm])

        # Concatenate the classwise distance matrices and transpose
        class_dm = np.concatenate(class_dm, axis=0)  # [C, N_test]
        class_dm = class_dm.transpose()  # [N_test, C]

        # Compute softmax probabilities
        class_dm_exp = np.exp(class_dm - class_dm.max())
        class_dm = class_dm_exp / np.sum(class_dm_exp, axis=-1, keepdims=True)

        probabilities = class_dm
        knn_labels = np.argmax(class_dm, axis=-1)

        return probabilities, knn_labels