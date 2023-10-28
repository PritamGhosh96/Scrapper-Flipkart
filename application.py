from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
import csv
import os
import time
from selenium import webdriver 
from selenium.webdriver.common.by import By # This needs to be used 

application = Flask(__name__) # initializing a flask app
app=application

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            DRIVER_PATH = r"chromedriver.exe"

            # Initialize the Chrome WebDriver
            driver = webdriver.Chrome(DRIVER_PATH)
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString

            driver.get(flipkart_url)
            flipkartPage = driver.page_source
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            driver.get(productLink)
            prodRes= driver.page_source
            driver.quit()
            prod_html = bs(prodRes, "html.parser")
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            filename = searchString + ".csv"
            with open(filename, "w", newline='', encoding='utf-8') as fw:
                headers = ["Price","Product","Customer Name", "Rating","Heading","Comment"]
                writer = csv.DictWriter(fw, fieldnames=headers)
                writer.writeheader()

                reviews = []
                for commentbox in commentboxes:
                    try:
                        price_element = flipkart_html.select('div._25b18c ._30jeq3')[0]
                        price = price_element.text
                    except:    
                        price = 'There is no price'
                    try:
                        #name.encode(encoding='utf-8')
                        name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                    except:
                        name = 'No Name'

                    try:
                        #rating.encode(encoding='utf-8')
                        rating = commentbox.div.div.div.div.text


                    except:
                        rating = 'No Rating'

                    try:
                        #commentHead.encode(encoding='utf-8')
                        commentHead = commentbox.div.div.div.p.text

                    except:
                        commentHead = 'No Comment Heading'
                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': ''})
                        #custComment.encode(encoding='utf-8')
                        custComment = comtag[0].div.text
                    except Exception as e:
                        print("Exception while creating dictionary: ",e)

                    mydict = {"Price": price,"Product": searchString, "Customer Name": name, "Rating": rating, "Heading": commentHead,"Comment": custComment}
                    reviews.append(mydict)
                   
                writer.writerows(reviews)

               
            client = pymongo.MongoClient("mongodb+srv://master:master123@atlascluster.w0iwrbk.mongodb.net/?retryWrites=true&w=majority")
            db = client['flipkart_scrap1']
            review_col = db['review_scrap_data']
            review_col.insert_many(reviews)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
	#app.run(debug=True)    