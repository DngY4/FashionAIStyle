import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from PIL import Image
import os

class FashionAITrainer:
    def __init__(self):
        self.fashion_data = self.load_fashion_data()
        self.image_data = []
        self.label_encoder = LabelEncoder()
        self.model = None

    def load_fashion_data(self):
        with open('fashion_knowledge.json', 'r') as f:
            return json.load(f)

    def preprocess_text_data(self, data):
        occasions = self.label_encoder.fit_transform(self.fashion_data['occasions'])
        styles = self.label_encoder.fit_transform(list(self.fashion_data['style_personalities'].keys()))
        return occasions, styles

    def load_image_data(self, directory):
        for filename in os.listdir(directory):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                img = Image.open(os.path.join(directory, filename))
                img = img.resize((224, 224))
                self.image_data.append(np.array(img))
        return np.array(self.image_data)

    def build_text_model(self, input_shape, num_classes):
        model = Sequential([
            Dense(256, activation='relu', input_shape=input_shape),
            Dropout(0.3),
            Dense(128, activation='relu'),
            Dropout(0.3),
            Dense(64, activation='relu'),
            Dropout(0.3),
            Dense(num_classes, activation='softmax')
        ])
        model.compile(optimizer=Adam(learning_rate=0.001),
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        return model

    def build_image_model(self, input_shape, num_classes):
        model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            Conv2D(64, (3, 3), activation='relu'),
            Flatten(),
            Dense(64, activation='relu'),
            Dense(num_classes, activation='softmax')
        ])
        model.compile(optimizer='adam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        return model

    def train_occasion_style_model(self):
        occasions, styles = self.preprocess_text_data(self.fashion_data)
        X_train, X_test, y_train, y_test = train_test_split(occasions, styles, test_size=0.2, random_state=42)
        
        num_classes = len(np.unique(styles))
        y_train = to_categorical(y_train, num_classes)
        y_test = to_categorical(y_test, num_classes)

        self.model = self.build_text_model((1,), num_classes)
        self.model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)

        loss, accuracy = self.model.evaluate(X_test, y_test)
        print(f"Occasion-Style Model - Test accuracy: {accuracy}")

    def train_image_classification_model(self, labels):
        image_data = self.load_image_data('fashion_images')
        X_train, X_test, y_train, y_test = train_test_split(image_data, labels, test_size=0.2, random_state=42)

        num_classes = len(np.unique(labels))
        y_train = to_categorical(y_train, num_classes)
        y_test = to_categorical(y_test, num_classes)

        self.model = self.build_image_model((224, 224, 3), num_classes)
        self.model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)

        loss, accuracy = self.model.evaluate(X_test, y_test)
        print(f"Image Classification Model - Test accuracy: {accuracy}")

    def save_model(self, filename):
        self.model.save(filename)

    def load_model(self, filename):
        from tensorflow.keras.models import load_model
        self.model = load_model(filename)

if __name__ == "__main__":
    trainer = FashionAITrainer()
    trainer.train_occasion_style_model()
    # Assuming we have image data and labels
    # trainer.train_image_classification_model(labels)
    trainer.save_model('fashion_ai_model.h5')