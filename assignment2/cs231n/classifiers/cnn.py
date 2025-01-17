import numpy as np

from cs231n.layers import *
from cs231n.fast_layers import *
from cs231n.layer_utils import *


class ThreeLayerConvNet(object):
  """
  A three-layer convolutional network with the following architecture:
  
  conv - relu - 2x2 max pool - affine - relu - affine - softmax
  
  The network operates on minibatches of data that have shape (N, C, H, W)
  consisting of N images, each with height H and width W and with C input
  channels.
  """
  
  def __init__(self, input_dim=(3, 32, 32), num_filters=32, filter_size=7,
               hidden_dim=100, num_classes=10, weight_scale=1e-3, reg=0.0,
               dtype=np.float32):
    """
    Initialize a new network.
    
    Inputs:
    - input_dim: Tuple (C, H, W) giving size of input data
    - num_filters: Number of filters to use in the convolutional layer
    - filter_size: Size of filters to use in the convolutional layer
    - hidden_dim: Number of units to use in the fully-connected hidden layer
    - num_classes: Number of scores to produce from the final affine layer.
    - weight_scale: Scalar giving standard deviation for random initialization
      of weights.
    - reg: Scalar giving L2 regularization strength
    - dtype: numpy datatype to use for computation.
    """
    self.params = {}
    self.reg = reg
    self.dtype = dtype
    
    ############################################################################
    # TODO: Initialize weights and biases for the three-layer convolutional    #
    # network. Weights should be initialized from a Gaussian with standard     #
    # deviation equal to weight_scale; biases should be initialized to zero.   #
    # All weights and biases should be stored in the dictionary self.params.   #
    # Store weights and biases for the convolutional layer using the keys 'W1' #
    # and 'b1'; use keys 'W2' and 'b2' for the weights and biases of the       #
    # hidden affine layer, and keys 'W3' and 'b3' for the weights and biases   #
    # of the output affine layer.                                              #
    ############################################################################
    C, H, W = input_dim
    F = num_filters
    P = (filter_size - 1) / 2
    S = 1

    ### Conv layer params
    HH, WW = filter_size, filter_size
    H_conv = (H + 2 * P - HH) / S + 1
    W_conv = (W + 2 * P - WW) / S + 1
    self.params['W1'] = weight_scale * np.random.randn(F, C, HH, WW)
    self.params['b1'] =np.zeros(F)

    ### Pool layer params
    h_pool, w_pool , S = 2, 2, 2
    H_pool = (H_conv - h_pool) / S + 1
    W_pool = (W_conv - w_pool) / S + 1

    ### Hidden affine layer params
    # from a pool layer of size (H_pool * W_pool) to size hidden_dim
    self.params['W2'] = weight_scale * np.random.randn(F * H_pool * W_pool, hidden_dim)
    self.params['b2'] = np.zeros(hidden_dim)

    ### Output affine layer params
    self.params['W3'] = weight_scale * np.random.randn(hidden_dim, num_classes)
    self.params['b3'] = np.zeros(num_classes)

    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################

    for k, v in self.params.iteritems():
      self.params[k] = v.astype(dtype)
     
 
  def loss(self, X, y=None):
    """
    Evaluate loss and gradient for the three-layer convolutional network.
    
    Input / output: Same API as TwoLayerNet in fc_net.py.
    """
    W1, b1 = self.params['W1'], self.params['b1']
    W2, b2 = self.params['W2'], self.params['b2']
    W3, b3 = self.params['W3'], self.params['b3']
    N = X.shape[0]
    
    # pass conv_param to the forward pass for the convolutional layer
    filter_size = W1.shape[2]
    conv_param = {'stride': 1, 'pad': (filter_size - 1) / 2}

    # pass pool_param to the forward pass for the max-pooling layer
    pool_param = {'pool_height': 2, 'pool_width': 2, 'stride': 2}

    scores = None
    ############################################################################
    # TODO: Implement the forward pass for the three-layer convolutional net,  #
    # computing the class scores for X and storing them in the scores          #
    # variable.                                                                #
    ############################################################################
    # Conv -> ReLU -> pool
    out_crp, cache_crp = conv_relu_pool_forward(X, W1, b1, conv_param, pool_param)

    # affine -> ReLu
    N, F, H_crp, W_crp = out_crp.shape
    out_ar, cache_ar = affine_relu_forward(out_crp.reshape(N, F * H_crp * W_crp), W2, b2)

    # affine
    scores, cache_scores = affine_forward(out_ar, W3, b3)
    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################
    
    if y is None:
      return scores
    
    loss, reg_loss, grads = 0, 0, {}
    ############################################################################
    # TODO: Implement the backward pass for the three-layer convolutional net, #
    # storing the loss and gradients in the loss and grads variables. Compute  #
    # data loss using softmax, and make sure that grads[k] holds the gradients #
    # for self.params[k]. Don't forget to add L2 regularization!               #
    ############################################################################
    scoreLoss, dscores = softmax_loss(scores, y)
    reg_loss += 0.5 * (self.reg * np.sum(W1*W1) + self.reg * np.sum(W2*W2) + self.reg * np.sum(W3*W3))
    loss = scoreLoss + reg_loss

    ### Backprop
    # affine <- softmax
    dx3, dW3, db3 = affine_backward(dscores, cache_scores)
    dW3 += self.reg * W3

    # affine + relu <- affine
    dx2, dW2, db2 = affine_relu_backward(dx3, cache_ar)
    dW2 += self.reg * W2

    # conv + relu + pool <- affine + relu
    dx2 = dx2.reshape(N, F, H_crp, W_crp)
    dx1, dW1, db1 = conv_relu_pool_backward(dx2, cache_crp)
    dW1 += self.reg * W1
    # dW1 = np.zeros(W1.shape)
    # db1 = np.zeros(b1.shape)

    grads.update({'W1': dW1, 'W2': dW2, 'W3': dW3,
                  'b1': db1, 'b2': db2, 'b3': db3})

    ############################################################################
    #                             END OF YOUR CODE                             #
    ############################################################################
    
    return loss, grads
  
  
pass
