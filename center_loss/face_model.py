import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.multiprocessing as mp
import torch.utils.model_zoo as model_zoo
from torchvision.models.resnet import BasicBlock, ResNet, model_urls
import math

class FaceModel(nn.Module):
    def __init__(self,num_classes, pretrained=False, **kwargs):
        super(FaceModel, self).__init__()
        self.model = ResNet(BasicBlock, [3, 4, 6, 3], **kwargs)
        if pretrained:
            parameters =  model_zoo.load_url(model_urls['resnet50'])
            self.model.load_state_dict(parameters)
        self.model.avgpool = None
        self.model.fc = nn.Linear(512*3*4, 512)
        self.model.classifier = nn.Linear(512, num_classes)
        self.centers = torch.zeros(num_classes, 512).type(torch.FloatTensor)
        self.num_classes = num_classes

    def forward(self, x):
        x = self.model.conv1(x)
        x = self.model.bn1(x)
        x = self.model.relu(x)
        x = self.model.maxpool(x)
        x = self.model.layer1(x)
        x = self.model.layer2(x)
        x = self.model.layer3(x)
        x = self.model.layer4(x)
        x = x.view(x.size(0), -1)
        x = self.model.fc(x)
        #feature for center loss
        self.features = x
        x = self.model.classifier(x)
        return x