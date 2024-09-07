from flask import Flask,render_template,request,flash,redirect
import psycopg2
from psycopg2 import extras,Error

app=Flask(__name__)
app.secret_key='abcxyz'
mydb=None
try:
    mydb=psycopg2.connect(
        host="localhost",
        user="postgres",
        password="Deepika@2004",
        database="contact-app",
        port=5432,        
    )
    mycursor=mydb.cursor()  
    

    mycursor.execute("""
                     create table if not exists contact(
                         id serial primary key,
                         name varchar(255) not null,
                         phone varchar(10) not null,
                         email varchar(120) unique,
                         address varchar(200)
                         )
                    """)
    
    
    
    
    
    mydb.commit()
    print("connected to database")
except Exception as e:
    print(f"Error: {e}")
    
@app.route('/')
def home():
    return render_template('add.html')

@app.route('/add',methods=['POST','GET'])
def add():
    if request.method=='POST':
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        address=request.form.get('address')
        try:
            mycursor=mydb.cursor()
            mycursor.execute("""
                             insert into contact(name,email,phone,address) values(%s, %s, %s, %s)""",(name,email,phone,address))
            mydb.commit()
            flash('Contact Added Successfully')
        except Exception as e:
            mydb.rollback()
            flash(f"Error in adding contact : {e}")
        finally :
            mycursor.close()
    return redirect('/contacts')

@app.route('/edit/<int:id>', methods=['POST', 'GET'])
def edit(id):
    
    contact = None

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')       
        
        try:
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * FROM contact WHERE id=%s", (id,))
            update_query = """
                UPDATE contact SET name=%s, email=%s, phone=%s, address=%s WHERE id=%s
            """
            mycursor.execute(update_query, (name, email, phone, address, id))
            
            mydb.commit()
        except Exception as e:
            mydb.rollback()
            flash(f"Error in updating contact: {e}")
            print(f"Error during update: {e}") 
        finally:
            mycursor.close()
        return redirect('/contacts') 
    else:
        try:
            mycursor = mydb.cursor(cursor_factory=extras.DictCursor)
            mycursor.execute("SELECT * FROM contact WHERE id=%s", (id,))
            contact = mycursor.fetchone()

            

            if contact is None:
                flash(f"Contact with ID {id} not found.")
                return redirect('/contacts')
        except Exception as e:
            flash(f"Error fetching contact: {e}")
            return redirect('/contacts')
        finally:
            mycursor.close()

    return render_template('edit.html', contact=contact)

@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    mycursor = mydb.cursor()
    mycursor.execute("delete FROM contact WHERE id=%s", (id,))
    mydb.commit()
    return redirect('/contacts')

@app.route('/contacts')
def contacts():
    try:
        mycursor=mydb.cursor(cursor_factory=extras.DictCursor)
        mycursor.execute("select * from contact")
        contacts=mycursor.fetchall()
    except Exception as e:
        contacts=[]
        flash(f"Error in fectching contacts :{e}")
    finally:
        mycursor.close()
    return render_template('contacts.html',contacts=contacts)         
    
if __name__ =='__main__':
  app.run(debug=True)