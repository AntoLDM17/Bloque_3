# Bloque_3

## A simple data analysis of the orders of a pizza restaurant in order to optimize the weekly ingredient purchases.
## Practica_2
This project consists of a simple pandas program which calculates the mode of the quantity spent each week for each ingredient.
Also, it supplies a data analysis of nulls and nans for each table.
This program makes use of pandas in order to calculate the quantity spent of ingredients every week. It also gives you a data analysis of nulls and nans for each file.
Added support for analyzing data from 2016. This new data had to be cleaned so I also added a new python script to do this.
New files to support this, were also created by modifying the original ones.

## XML
Added support to save data into XML files. This files include a data typology analysis and the final reccomendation.

### Instructions:
To execute the program, Use pip install -r requirements.txt to download the libraries needed. Then run "pizzas_maven_XML.py".
Also, it is possible to create a docker image to deploy the program in a safer way.
To do that, just run the following command in the console, inside the directory where you clone this repository:

docker build . -t Bloque_3/practica_2

