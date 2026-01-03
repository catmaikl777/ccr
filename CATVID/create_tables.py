#!/usr/bin/env python
import os
import sys
import django
import sqlite3

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CATVID.settings')
django.setup()

def create_tables():
    # Подключаемся к базе данных
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создаем таблицу Box
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main_box (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            price INTEGER NOT NULL,
            image VARCHAR(100) NOT NULL DEFAULT 'box.png',
            is_active BOOLEAN NOT NULL DEFAULT 1
        )
    ''')
    
    # Создаем таблицу BoxDrop
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main_boxdrop (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            box_id INTEGER NOT NULL,
            item_type VARCHAR(10) NOT NULL,
            item_value VARCHAR(100) NOT NULL,
            drop_chance REAL NOT NULL,
            is_rare BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (box_id) REFERENCES main_box (id)
        )
    ''')
    
    # Создаем таблицу BoxOpening
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main_boxopening (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            box_id INTEGER NOT NULL,
            item_type VARCHAR(10) NOT NULL,
            item_value VARCHAR(100) NOT NULL,
            is_rare BOOLEAN NOT NULL DEFAULT 0,
            opened_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES main_player (id),
            FOREIGN KEY (box_id) REFERENCES main_box (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Таблицы созданы успешно!")

if __name__ == '__main__':
    create_tables()