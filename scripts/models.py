# Copyright © 2023-2024 Apple Inc.

import math
from typing import Optional

import mlx.core as mx
import mlx.nn as nn


class LoRALinear(nn.Module):
    """
    A LoRA (Low-Rank Adaptation) linear layer that wraps an existing linear layer.
    Works with any model architecture (Llama, Mistral, Gemma, etc.)
    """
    
    @staticmethod
    def from_linear(linear: nn.Linear, rank: int = 8, scale: float = 20.0):
        """
        Create a LoRALinear from an existing nn.Linear or nn.QuantizedLinear.
        
        Args:
            linear: The existing linear layer to wrap
            rank: The rank of the LoRA decomposition
            scale: The scaling factor for the LoRA update
        """
        # Get dimensions from the linear layer
        output_dims, input_dims = linear.weight.shape
        if isinstance(linear, nn.QuantizedLinear):
            input_dims *= 32 // linear.bits
        
        lora_lin = LoRALinear(input_dims, output_dims, rank, scale=scale)
        lora_lin.linear = linear
        return lora_lin

    def to_linear(self):
        """
        Fuse the LoRA weights back into the linear layer.
        Returns a new linear layer with the LoRA updates baked in.
        """
        linear = self.linear
        bias = "bias" in linear
        weight = linear.weight
        is_quantized = isinstance(linear, nn.QuantizedLinear)

        # Use the same type as the linear weight if not quantized
        dtype = weight.dtype

        if is_quantized:
            dtype = mx.float16
            weight = mx.dequantize(
                weight,
                linear.scales,
                linear.biases,
                linear.group_size,
                linear.bits,
            )
        output_dims, input_dims = weight.shape
        fused_linear = nn.Linear(input_dims, output_dims, bias=bias)

        lora_b = (self.scale * self.lora_b.T).astype(dtype)
        lora_a = self.lora_a.T.astype(dtype)
        fused_linear.weight = weight + lora_b @ lora_a
        if bias:
            fused_linear.bias = linear.bias

        if is_quantized:
            fused_linear = nn.QuantizedLinear.from_linear(
                fused_linear,
                linear.group_size,
                linear.bits,
            )

        return fused_linear

    def __init__(
        self,
        input_dims: int,
        output_dims: int,
        lora_rank: int = 8,
        bias: bool = False,
        scale: float = 20.0,
    ):
        super().__init__()

        # Regular linear layer weights
        self.linear = nn.Linear(input_dims, output_dims, bias=bias)

        # Scale for low-rank update
        self.scale = scale

        # Low rank lora weights
        lora_scale = 1 / math.sqrt(input_dims)
        self.lora_a = mx.random.uniform(
            low=-lora_scale,
            high=lora_scale,
            shape=(input_dims, lora_rank),
        )
        self.lora_b = mx.zeros(shape=(lora_rank, output_dims))

    def __call__(self, x):
        dtype = self.linear.weight.dtype
        if isinstance(self.linear, nn.QuantizedLinear):
            dtype = self.linear.scales.dtype
        y = self.linear(x.astype(dtype))
        z = (x @ self.lora_a) @ self.lora_b
        return y + self.scale * z
