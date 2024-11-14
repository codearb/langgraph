import os
import random
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    email = Column(String, unique=True, index=True)

    orders = relationship("Order", back_populates="user")

class Food(Base):
    __tablename__ = "food"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    price = Column(Float)
    orders = relationship("Order", back_populates="food")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("food.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="orders")
    food = relationship("Food", back_populates="orders")

DATABASE_URL = "sqlite:///example.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def generate_sample_data(num_users=1000, num_foods=15, num_orders=10000):
    session = SessionLocal()

    # Generate users
    users = []
    for _ in range(num_users):
        name = f"User {len(users) + 1}"
        age = random.randint(18, 65)
        email = f"{name.lower().replace(' ', '.')}@example.com"
        users.append(User(name=name, age=age, email=email))
    session.add_all(users)
    session.commit()

    # Generate foods
    foods = []
    for _ in range(num_foods):
        name = f"Food {len(foods) + 1}"
        price = round(random.uniform(5.0, 50.0), 2)
        foods.append(Food(name=name, price=price))
    session.add_all(foods)
    session.commit()

    # Generate orders
    orders = []
    for _ in range(num_orders):
        food_id = random.randint(1, num_foods)
        user_id = random.randint(1, num_users)
        orders.append(Order(food_id=food_id, user_id=user_id))
    session.add_all(orders)
    session.commit()

    session.close()
    print(f"Successfully generated {num_users} users, {num_foods} foods, and {num_orders} orders.")

if __name__ == "__main__":
    if not os.path.exists("example.db"):
        init_db()
        generate_sample_data(num_users=1000, num_foods=15, num_orders=10000)
    else:
        print("The 'example.db' database already exists.")