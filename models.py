import nn

class PerceptronModel(object):
    def __init__(self, dimensions):
        """
        Initialize a new Perceptron instance.

        A perceptron classifies data points as either belonging to a particular
        class (+1) or not (-1). `dimensions` is the dimensionality of the data.
        For example, dimensions=2 would mean that the perceptron must classify
        2D points.
        """
        self.w = nn.Parameter(1, dimensions)

    def get_weights(self):
        """
        Return a Parameter instance with the current weights of the perceptron.
        """
        return self.w

    def run(self, x):
        """
        Calculates the score assigned by the perceptron to a data point x.

        Inputs:
            x: a node with shape (1 x dimensions)
        Returns: a node containing a single number (the score)
        """
        "*** YOUR CODE HERE ***"
        return nn.DotProduct(self.w, x)

    def get_prediction(self, x):
        """
        Calculates the predicted class for a single data point `x`.

        Returns: 1 or -1
        """
        "*** YOUR CODE HERE ***"
        return (nn.as_scalar(self.run(x)) >= 0) - (nn.as_scalar(self.run(x)) < 0)

    def train(self, dataset):
        """
        Train the perceptron until convergence.
        """
        "*** YOUR CODE HERE ***"
        flag = True
        while flag:
            flag = not flag # must meet predection to continue
            for large, small in dataset.iterate_once(1): #large is a 1x2 matrix, small is a 1x1 matrix
                if self.get_prediction(large) != nn.as_scalar(small):
                    flag = True     # reset the flag
                    # self.w.update(nn.Constant(nn.as_scalar(small)*large.data), 1)
                    nn.Parameter.update(self.w, large, nn.as_scalar(small))
                    # updates the parameter using large and small to do the thing, with 1
                    # being the dimensionallity? Not sure...

class RegressionModel(object):
    """
    A neural network model for approximating a function that maps from real
    numbers to real numbers. The network should be sufficiently large to be able
    to approximate sin(x) on the interval [-2pi, 2pi] to reasonable precision.
    """
    def __init__(self):
        # Initialize your model parameters here
        "*** YOUR CODE HERE ***"
        from nn import Parameter as P
        UPPER, LOWER, MINUM = 250, 125, 1
        self.multiplier = -(MINUM/10)   # number must be negative
        self.params = [ P(MINUM, UPPER), # w1
                        P(UPPER, LOWER), # w2
                        P(LOWER, MINUM), # w3
                        P(MINUM, UPPER), # b1
                        P(MINUM, LOWER), # b2
                        P(MINUM, MINUM), # b3
                      ]

    def run(self, x):
        """
        Runs the model for a batch of examples.

        Inputs:
            x: a node with shape (batch_size x 1)
        Returns:
            A node with shape (batch_size x 1) containing predicted y-values
        """
        "*** YOUR CODE HERE ***"
        from nn import ReLU    as R
        from nn import Linear  as L
        from nn import AddBias as B
        a =  R(B(L(x, self.params[0]), self.params[3])) # w1, b1
        b =  R(B(L(a, self.params[1]), self.params[4])) # w2, b2
        return B(L(b, self.params[2]), self.params[5])  # w3, b3

    def get_loss(self, x, y):
        """
        Computes the loss for a batch of examples.

        Inputs:
            x: a node with shape (batch_size x 1)
            y: a node with shape (batch_size x 1), containing the true y-values
                to be used for training
        Returns: a loss node
        """
        "*** YOUR CODE HERE ***"
        return nn.SquareLoss(self.run(x), y)

    def train(self, dataset):
        """
        Trains the model.
        """
        "*** YOUR CODE HERE ***"
        LOSS_TOLEREN = .001
        DATASET_SIZE = 200
        loss = LOSS_TOLEREN * 10 # loss must be > than LOSS_TOLEREN
        # while True:
        while loss > LOSS_TOLEREN:
            for x, y in dataset.iterate_once(DATASET_SIZE):
                loss  = self.get_loss(x, y) # x and y are the same size here, LOWERxMINUM
                grads = nn.gradients(self.get_loss(x, y), self.params)
                for param, grad in zip(self.params, grads):
                    param.update(grad, self.multiplier)
                loss  = nn.as_scalar(loss)  #update before next iteration
            # if loss > LOSS_TOLEREN:
            #     break

class DigitClassificationModel(object):
    """
    A model for handwritten digit classification using the MNIST dataset.

    Each handwritten digit is a 28x28 pixel grayscale image, which is flattened
    into a 784-dimensional vector for the purposes of this model. Each entry in
    the vector is a floating point number between 0 and 1.

    The goal is to sort each digit into one of 10 classes (number 0 through 9).

    (See RegressionModel for more information about the APIs of different
    methods here. We recommend that you implement the RegressionModel before
    working on this part of the project.)
    """
    def __init__(self):
        # Initialize your model parameters here
        "*** YOUR CODE HERE ***"
        from nn import Parameter as P
        UPPER, MID, LOWER, MINUM = 784, 100, 10, 1
        self.multiplier = -(MINUM/200)   # number must be negative
        self.batch_size = 1

        self.params = [ P(UPPER, MID), # w1
                        P(MID, LOWER), # w2
                        P(MINUM, MID), # b1
                        P(MINUM, LOWER), # b2
                      ]

    def run(self, x):
        """
        Runs the model for a batch of examples.

        Your model should predict a node with shape (batch_size x 10),
        containing scores. Higher scores correspond to greater probability of
        the image belonging to a particular class.

        Inputs:
            x: a node with shape (batch_size x 784)
        Output:
            A node with shape (batch_size x 10) containing predicted scores
                (also called logits)
        """
        "*** YOUR CODE HERE ***"
        from nn import ReLU    as R
        from nn import Linear  as L
        from nn import AddBias as B
        a =  R(B(L(x, self.params[0]), self.params[2])) # w1, b1
        b =  R(B(L(a, self.params[1]), self.params[3])) # w2, b2
        return b

    def get_loss(self, x, y):
        """
        Computes the loss for a batch of examples.

        The correct labels `y` are represented as a node with shape
        (batch_size x 10). Each row is a one-hot vector encoding the correct
        digit class (0-9).

        Inputs:
            x: a node with shape (batch_size x 784)
            y: a node with shape (batch_size x 10)
        Returns: a loss node
        """
        "*** YOUR CODE HERE ***"
        return nn.SoftmaxLoss(self.run(x), y)

    def train(self, dataset):
        """
        Trains the model.
        """
        "*** YOUR CODE HERE ***"

        while True:
            for x, y in dataset.iterate_once(self.batch_size):
                loss  = self.get_loss(x, y) # x and y are the same size here, LOWERxMINUM
                grads = nn.gradients(self.get_loss(x, y), self.params)
                for param, grad in zip(self.params, grads):
                    param.update(grad, self.multiplier)
                loss  = nn.as_scalar(loss)  #update before next iteration
            if dataset.get_validation_accuracy() >= 0.97:
                return
