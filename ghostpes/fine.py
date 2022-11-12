import pytorch_lightning as pl
from torchvision import transforms 

import pytorch_lightning as pl
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import random_split, DataLoader
from torchvision.datasets import ImageFolder
from torchmetrics import Accuracy, Precision, Recall

from torchvision import transforms
from model import model_ghost_git
import albumentations as A
from albumentations.pytorch import ToTensorV2
import numpy as np




transform_train = A.Compose([
    A.Blur(),
    A.Cutout(),
    A.ISONoise(p=0.7),
    A.RandomBrightnessContrast(),
    A.ColorJitter(),
    A.HorizontalFlip(),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ToTensorV2(),
])

transform_valid = A.Compose([
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ToTensorV2(),
])

def trans_func_train(image):
    image = np.asarray(image)
    image_aug = transform_train(image=image)['image']
    return image_aug

def trans_func_valid(image):
    image = np.asarray(image)
    image_aug = transform_valid(image=image)['image']
    return image_aug



class PesDataModule(pl.LightningDataModule):
    def __init__(self, batch_size, data_dir: str = './'):
        super().__init__()
        self.batch_size = batch_size

        self.transform_train = trans_func_train

        self.transform_valid = trans_func_valid
        
        self.num_classes = 2

    def setup(self, stage=None):
        if stage == 'fit' or stage is None:
            self.data_train = ImageFolder("/content/dataset/train", transform=self.transform_train)
            self.data_val = ImageFolder("/content/dataset/valid", transform=self.transform_valid)

    def train_dataloader(self):
        return DataLoader(self.data_train, batch_size=self.batch_size, shuffle=True)

    def val_dataloader(self):
        return DataLoader(self.data_val, batch_size=self.batch_size)

    # def test_dataloader(self):
    #     return DataLoader(self.cifar_test, batch_size=self.batch_size)


class LitModel(pl.LightningModule):
    def __init__(self):
        super().__init__()
        
        # log hyperparameters
        # model = MobileViT(opts)
        # model.classifier.fc = Identity()
        # model.load_state_dict(new_dict)

        # model = MobileViT(opts)
        # model.load_state_dict(torch.load("mobilevit_xxs.pt"))
        model = model_ghost_git

        # model = torchvision.models.mobilenet_v2(pretrained=True)

        model.classifier.fc = nn.Linear(320, 2)

        self.model = model

        self.accuracy = Accuracy()
        self.pre = Precision(num_classes=2)
        self.rec = Recall(num_classes=2)
    
    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self.model(x)
        loss = F.cross_entropy(logits, y)
        
        preds = torch.argmax(logits, dim=1)
        acc = self.accuracy(preds, y)
        pre = self.pre(preds, y)
        rec = self.rec(preds, y)
        self.log('train_loss', loss, on_step=False, on_epoch=True, logger=True)
        self.log('train_acc', acc, on_step=False, on_epoch=True, logger=True)
        self.log('train_pre', pre, on_step=False, on_epoch=True, logger=True)
        self.log('train_rec', rec, on_step=False, on_epoch=True, logger=True)
        
        return loss
    
    def validation_step(self, batch, batch_idx):
        x, y = batch
        logits = self.model(x)
        loss = F.cross_entropy(logits, y)

        # validation metrics
        preds = torch.argmax(logits, dim=1)
        acc = self.accuracy(preds, y)
        pre = self.pre(preds, y)
        rec = self.rec(preds, y)
        self.log('val_loss', loss, prog_bar=True, on_step=False, on_epoch=True)
        self.log('val_acc', acc, prog_bar=True, on_step=False, on_epoch=True)
        self.log('val_pre', pre, on_step=False, on_epoch=True, logger=True)
        self.log('val_rec', rec, on_step=False, on_epoch=True, logger=True)
        return loss
    
    # def test_step(self, batch, batch_idx):
    #     x, y = batch
    #     logits = self.model(x)
    #     loss = F.cross_entropy(logits, y)
        
    #     # validation metrics
    #     preds = torch.argmax(logits, dim=1)
    #     acc = self.accuracy(preds, y)
    #     self.log('test_loss', loss, prog_bar=True, on_step=False, on_epoch=True)
    #     self.log('test_acc', acc, prog_bar=True, on_step=False, on_epoch=True)
    #     return loss
    
    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=1e-4)
        return optimizer


dm = PesDataModule(batch_size=32)

model_lit = LitModel()

# early_stop_callback = pl.callbacks.EarlyStopping(monitor="val_loss")
checkpoint_callback = pl.callbacks.ModelCheckpoint()

from pytorch_lightning.loggers import WandbLogger

wandb_logger = WandbLogger(project="MocoSau_fine_tune_3", name="ghost_2")


# Initialize a trainer
trainer = pl.Trainer(max_epochs=100,
                     gpus=1, 
                    #  step-
                    # limit_train_batches=0.3,
                     logger=wandb_logger,
                    #  callbacks=[early_stop_callback,
                    #             # ImagePredictionLogger(val_samples),
                    #             checkpoint_callback],
                     )

# Train the model ⚡🚅⚡
trainer.fit(model_lit, dm)