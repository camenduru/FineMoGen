_base_ = ['../_base_/datasets/inter_human_bs128.py']

# checkpoint saving
checkpoint_config = dict(interval=1)

dist_params = dict(backend='nccl')
log_level = 'INFO'
load_from = None
resume_from = None
workflow = [('train', 1)]

# optimizer
optimizer = dict(type='Adam', lr=2e-4)
optimizer_config = dict(grad_clip=None)
# learning policy
lr_config = dict(policy='CosineAnnealing', min_lr_ratio=2e-5, by_epoch=False)
runner = dict(type='EpochBasedRunner', max_epochs=40)

log_config = dict(
    interval=50,
    hooks=[
        dict(type='TextLoggerHook'),
        # dict(type='TensorboardLoggerHook')
    ])

input_feats = 524
max_seq_len = 300
latent_dim = 512
time_embed_dim = 2048
text_latent_dim = 256
ff_size = 1024
num_heads = 8
dropout = 0

# model settings
model = dict(type='MotionDiffusion',
             model=dict(
                 type='ReMoDiffuseTransformer',
                 input_feats=input_feats,
                 max_seq_len=max_seq_len,
                 latent_dim=latent_dim,
                 time_embed_dim=time_embed_dim,
                 num_layers=4,
                 ca_block_cfg=dict(type='SemanticsModulatedAttention',
                                   latent_dim=latent_dim,
                                   text_latent_dim=text_latent_dim,
                                   num_heads=num_heads,
                                   dropout=dropout,
                                   time_embed_dim=time_embed_dim),
                 ffn_cfg=dict(latent_dim=latent_dim,
                              ffn_dim=ff_size,
                              dropout=dropout,
                              time_embed_dim=time_embed_dim),
                 text_encoder=dict(pretrained_model='clip',
                                   latent_dim=text_latent_dim,
                                   num_layers=2,
                                   ff_size=2048,
                                   dropout=dropout,
                                   use_text_proj=False),
                 retrieval_cfg=dict(
                     num_retrieval=1,
                     stride=4,
                     num_layers=2,
                     num_motion_layers=2,
                     kinematic_coef=0.1,
                     topk=1,
                     retrieval_file='data/database/interhuman_text_train.npz',
                     latent_dim=latent_dim,
                     output_dim=latent_dim,
                     max_seq_len=max_seq_len,
                     num_heads=num_heads,
                     ff_size=ff_size,
                     dropout=dropout,
                     ffn_cfg=dict(
                         latent_dim=latent_dim,
                         ffn_dim=ff_size,
                         dropout=dropout,
                     ),
                     sa_block_cfg=dict(type='EfficientSelfAttention',
                                       latent_dim=latent_dim,
                                       num_heads=num_heads,
                                       dropout=dropout),
                 ),
                 scale_func_cfg=dict(coarse_scale=6.5,
                                     both_coef=0.52351,
                                     text_coef=-0.28419,
                                     retr_coef=2.39872),
                 post_process_cfg=dict(
                     unnormalized_infer=True,
                     mean_path='data/datasets/inter_human/mean.npy',
                     std_path='data/datasets/inter_human/std.npy')),
             loss_recon=dict(type='MSELoss', loss_weight=1, reduction='none'),
             loss_reduction="batch",
             diffusion_train=dict(
                 beta_scheduler='linear',
                 diffusion_steps=1000,
                 model_mean_type='start_x',
                 model_var_type='fixed_large',
             ),
             diffusion_test=dict(
                 beta_scheduler='linear',
                 diffusion_steps=1000,
                 model_mean_type='start_x',
                 model_var_type='fixed_large',
                 respace='15,15,8,6,6',
             ),
             inference_type='ddim')
data = dict(samples_per_gpu=64)
