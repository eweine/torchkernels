import torch

class RFF:

	def __init__(self, 
		input_dim:int, 
		num_features:int, 
		length_scale:float=1., 
		shape_matrix:torch.Tensor=None,
		bias_term:bool=False, 
		device:str=None):	
		"""Initialize an instance of the RFF class.

		Parameters
		----------
		input_dim : int
			input dimension of the data.
		num_features : int
			number of random features to generate.
		length_scale : float
			kernel length scale, defaults to 1.
		shape_matrix : torch.Tensor
			shape matrix for the random features, defaults to None. Shape matrix entered must be symmetric, positive definite and of dimension d x d where d is input dimension.
		bias_term : bool
			whether to include a bias term in the random features, defaults to False.
		device : str
			which device to use, can be 'cpu' or 'cuda', defaults to None which means use cuda if available.
		"""
		if device is None:
			self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
		else:
			self.device = torch.device(device)
		self.input_dim = input_dim
		self.num_features = num_features
		self.length_scale = length_scale
		if shape_matrix is not None:
			self.shape_matrix = shape_matrix
			assert self.shape_matrix.shape[0] == self.shape_matrix.shape[1] == self.input_dim, "Shape matrix must be square and of dimension d x d where d is input dimension."
			self.sqrt_M = torch.linalg.cholesky(self.shape_matrix.to(self.device))
		else:
			self.sqrt_M = None
			self.shape_matrix = None
		self.bias_term = bias_term

		self.c1 = torch.sqrt(torch.tensor(2 / self.num_features)).to(self.device)
		if not self.bias_term:
			self._num_features = self.num_features//2
		else: 
			self._num_features = self.num_features

		self.W1 = (torch.randn(self.input_dim,self._num_features,device=self.device)/self.length_scale)
		self.set_W2()
		if self.bias_term:
			self._bias = (torch.rand(self._num_features) * torch.pi * 2).to(self.device)
	
	def __call__(self, x):
		x = x.to(self.device)
		if self.shape_matrix is not None:
			x = torch.mm(x, self.sqrt_M)
		return self.apply_W2(torch.mm(x, self.W1))

	def set_W1(self, W1=None):
		if W1 is not None:
			self.W1=W1

	def set_W2(self):
		raise NotImplementedError("This method must be implemented in the subclass")

	def apply_W2(self):
		raise NotImplementedError("This method must be implemented in the subclass")

	def update_shape(self, shape_matrix):
		self.shape_matrix = shape_matrix
		self.sqrt_M = torch.linalg.cholesky(self.shape_matrix.to(self.device))
