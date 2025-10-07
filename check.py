import torch

# This will print True if PyTorch can see your GPU, and False otherwise.
print(torch.cuda.is_available())