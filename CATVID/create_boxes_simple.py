from main.models import Box, BoxDrop

# Удаляем старые ящики
Box.objects.all().delete()

# Создаем базовый ящик
basic_box = Box.objects.create(
    name='Базовый ящик',
    description='Простой ящик с базовыми наградами',
    price=100,
    image='box.png',
    is_active=True
)

# Создаем премиум ящик
premium_box = Box.objects.create(
    name='Премиум ящик',
    description='Улучшенный ящик с редкими наградами',
    price=300,
    image='box.png',
    is_active=True
)

# Содержимое базового ящика
BoxDrop.objects.create(box=basic_box, item_type='coins', item_value='50', drop_chance=40.0, is_rare=False)
BoxDrop.objects.create(box=basic_box, item_type='clicks', item_value='100', drop_chance=30.0, is_rare=False)
BoxDrop.objects.create(box=basic_box, item_type='skin', item_value='skin3.png', drop_chance=15.0, is_rare=False)
BoxDrop.objects.create(box=basic_box, item_type='skin', item_value='skin4.png', drop_chance=10.0, is_rare=True)
BoxDrop.objects.create(box=basic_box, item_type='skin', item_value='skin5.png', drop_chance=5.0, is_rare=True)

# Содержимое премиум ящика
BoxDrop.objects.create(box=premium_box, item_type='coins', item_value='200', drop_chance=30.0, is_rare=False)
BoxDrop.objects.create(box=premium_box, item_type='clicks', item_value='300', drop_chance=25.0, is_rare=False)
BoxDrop.objects.create(box=premium_box, item_type='skin', item_value='skin5.png', drop_chance=20.0, is_rare=False)
BoxDrop.objects.create(box=premium_box, item_type='skin', item_value='skin6.png', drop_chance=15.0, is_rare=True)
BoxDrop.objects.create(box=premium_box, item_type='skin', item_value='skin7.png', drop_chance=8.0, is_rare=True)
BoxDrop.objects.create(box=premium_box, item_type='skin', item_value='skin8.png', drop_chance=2.0, is_rare=True)

print("Ящики созданы!")
print(f"Всего ящиков: {Box.objects.count()}")
for box in Box.objects.all():
    print(f"- {box.name}: {box.price} монет, содержимое: {box.drops.count()} предметов")