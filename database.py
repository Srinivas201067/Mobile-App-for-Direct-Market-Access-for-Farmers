from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg2://root:bth63051zF4pptj6ytBjVofIewGkupaZ@dpg-csseg29u0jms73ea4kf0-a.oregon-postgres.render.com/dma_app?sslmode=require"
)


def remove_Product(pid):
    with engine.connect() as conn:
        result = conn.execute(text("DELETE FROM products WHERE pid = :pid"),
                              {"pid": pid})
        conn.commit()


def accept_order(oid, pid, quantity):
    with engine.connect() as conn:
        try:
            # Update the order status
            conn.execute(
                text(
                    "UPDATE orders SET status = 'Accepted', updates = 'Accepted' WHERE oid = :oid"
                ), {"oid": oid})

            # Update the product quantity
            conn.execute(
                text(
                    "UPDATE products SET quantity = COALESCE(quantity, 0) - :quantity WHERE pid = :pid"
                ), {
                    "pid": pid,
                    "quantity": quantity
                })

            conn.commit()
        except Exception as e:
            print(f"Error updating orders or products: {e}")


def update(oid, update_order):
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE orders SET updates=:update_order WHERE oid=:oid"), {
                "oid": oid,
                "update_order": update_order
            })
        conn.commit()


def cancel_order(oid):
    with engine.connect() as conn:
        conn.execute(text("UPDATE orders SET status='Cancel' WHERE oid=:oid"),
                     {"oid": oid})
        conn.commit()


def delivered_order(oid, pid, rating):
    with engine.connect() as conn:
        try:
            # Update the order status
            conn.execute(
                text(
                    "UPDATE orders SET status = 'Delivered', updates = 'Delivered' WHERE oid = :oid"
                ), {"oid": oid})

            conn.execute(
                text("""
                    UPDATE products
                    SET rating = 
                        CASE 
                            WHEN rating IS NULL THEN :rating
                            ELSE (rating + :rating) / 2
                        END
                    WHERE pid = :pid
                    """), {
                    "rating": rating,
                    "pid": pid
                })

            conn.commit()
        except Exception as e:
            print(f"Error delivering order or updating product rating: {e}")
            conn.rollback()


def add_user_to_db(data):
    with engine.connect() as conn:
        query = text(
            "INSERT INTO products(fname, fid, pname, quantity, price, dt,url) "
            "VALUES(:fname, :fid, :pname, :quantity, :price, :dt,:url)")
        conn.execute(
            query,
            {
                "fname": username,
                "fid": uid,
                "pname": data["pname"],
                "quantity": data["quantity"],
                "price": data["price"],
                "dt": data["date"],
                "url": data['url']
            },
        )
        conn.commit()


def add_product_to_db(data, username, uid):

    with engine.connect() as conn:
        query = text(
            "INSERT INTO products(fname, fid, pname, quantity, price, dt,url) "
            "VALUES(:fname, :fid, :pname, :quantity, :price, :dt,:url)")
        conn.execute(
            query,
            {
                "fname": username,
                "fid": uid,
                "pname": data["pname"],
                "quantity": data["quantity"],
                "price": data["price"],
                "dt": data["date"],
                "url": data['url']
            },
        )
        conn.commit()


def add_orders_to_db(fid, pid, bid, quantity, total_price):
    with engine.begin() as conn:  # Transactional connection
        query = text(
            "INSERT INTO Orders(fid, pid, bid, quantity, price, status) "
            "VALUES(:fid, :pid, :bid, :quantity, :price, 'Ordered')")
        conn.execute(
            query, {
                "fid": fid,
                "pid": pid,
                "bid": bid,
                "quantity": quantity,
                "price": total_price,
            })


def insert_message_into_db(fid, bid, pid, mesg):
    try:
        with engine.connect() as conn:
            query = text("""
                INSERT INTO chats(fid, bid, pid, mesg, sentat)
                VALUES (:fid, :bid, :pid, :mesg, :time)
            """)
            conn.execute(
                query,
                {
                    "fid": fid,
                    "bid": bid,
                    "pid": pid,
                    "mesg": mesg,
                    "time": datetime.now(),  # Current timestamp
                })
    except Exception as e:
        import traceback
        print(f"Error inserting message: {e}\n{traceback.format_exc()}")
