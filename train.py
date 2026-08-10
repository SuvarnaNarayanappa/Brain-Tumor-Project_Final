import os
import torch
import torch.nn as nn
import torch.optim as optim

from torchvision.models import resnet50
from torchvision import datasets, transforms
from torch.utils.data import DataLoader


TRAIN_DIR = "./data/Training"
TEST_DIR = "./data/Testing"

MODEL_PATH = "./models/bt_resnet50_model.pt"

BATCH_SIZE = 16
EPOCHS = 1
LEARNING_RATE = 0.0001

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Using device:", DEVICE)


# Map dataset folders to the label order expected by app.py
FOLDER_TO_APP_LABEL_INDEX = {
    "no_tumor": 0,
    "meningioma_tumor": 1,
    "glioma_tumor": 2,
    "pituitary_tumor": 3,
}


# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])


# Load datasets
train_dataset = datasets.ImageFolder(
    TRAIN_DIR,
    transform=transform
)

test_dataset = datasets.ImageFolder(
    TEST_DIR,
    transform=transform
)

print("Original ImageFolder mapping:")
print(train_dataset.class_to_idx)

print("Training images:", len(train_dataset))
print("Testing images:", len(test_dataset))


# Remap ImageFolder labels
def remap_dataset_labels(dataset):

    new_targets = []

    for path, original_index in dataset.samples:

        folder_name = os.path.basename(
            os.path.dirname(path)
        )

        new_index = FOLDER_TO_APP_LABEL_INDEX[folder_name]

        new_targets.append(new_index)

    return new_targets


train_dataset.targets = remap_dataset_labels(train_dataset)
test_dataset.targets = remap_dataset_labels(test_dataset)


# Data loaders
train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=2
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=2
)


# Exact ResNet50 architecture expected by app.py
print("Creating ResNet50 model...")

model = resnet50(pretrained=True)

n_inputs = model.fc.in_features

model.fc = nn.Sequential(
    nn.Linear(n_inputs, 2048),
    nn.SELU(),
    nn.Dropout(p=0.4),

    nn.Linear(2048, 2048),
    nn.SELU(),
    nn.Dropout(p=0.4),

    nn.Linear(2048, 4),
    nn.LogSigmoid(),
)

model = model.to(DEVICE)


# Loss and optimizer
criterion = nn.NLLLoss()

optimizer = optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)


# Training
print("Starting training...")

for epoch in range(EPOCHS):

    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for batch_index, (images, labels) in enumerate(train_loader):

        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, labels)

        loss.backward()

        optimizer.step()

        running_loss += loss.item()

        _, predicted = torch.max(outputs.data, 1)

        total += labels.size(0)

        correct += (predicted == labels).sum().item()

        if batch_index % 20 == 0:

            print(
                f"Epoch [{epoch + 1}/{EPOCHS}] "
                f"Batch [{batch_index}/{len(train_loader)}] "
                f"Loss: {loss.item():.4f}"
            )

    accuracy = 100 * correct / total

    print(
        f"Epoch [{epoch + 1}/{EPOCHS}] "
        f"Loss: {running_loss / len(train_loader):.4f} "
        f"Accuracy: {accuracy:.2f}%"
    )


# Save model
os.makedirs("./models", exist_ok=True)

torch.save(
    model.state_dict(),
    MODEL_PATH
)

print("Training complete.")
print("Model saved to:", MODEL_PATH)
