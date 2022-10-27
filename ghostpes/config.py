import argparse

num_workers = 2
img_size = 224
batch_size = 128
memory_bank_size = 2048
seed = 1
max_epochs = 200

path_to_train = "frame_video_sau"


opts = argparse.Namespace()

setattr(opts,"model.classification.name","mobilevit")
setattr(opts,"model.classification.classifier_dropout", 0.1)

setattr(opts,"model.classification.mit.mode" ,"xx_small")
setattr(opts,"model.classification.mit.ffn_dropout", 0.0)
setattr(opts,"model.classification.mit.attn_dropout", 0.0)
setattr(opts,"model.classification.mit.dropout", 0.05)
setattr(opts,"model.classification.mit.number_heads", 4)
setattr(opts,"model.classification.mit.no_fuse_local_global_features", False)
setattr(opts,"model.classification.mit.conv_kernel_size", 3)

setattr(opts,"model.classification.activation.name", "swish")

setattr(opts,"model.normalization.name", "batch_norm_2d")
setattr(opts,"model.normalization.momentum", 0.1)

setattr(opts,"model.activation.name", "swish")

setattr(opts,"model.activation.layer.global_pool", "mean")
setattr(opts,"model.activation.layer.conv_init", "kaiming_normal")
setattr(opts,"model.activation.layer.linear_init", "trunc_normal")
setattr(opts,"model.activation.layer.linear_init_std_dev", 0.02)