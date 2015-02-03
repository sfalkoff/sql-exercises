1

-----

Write a query that shows all the information about all the salespeople in
the database. Use a basic SELECT query.

-----

SELECT * FROM salespeople;


==========
2

-----

Write a query that shows all the information about all salespeople from
the 'Northwest' region.

-----

SELECT * FROM salespeople WHERE region='Northwest';


==========
3

-----

Write a query that shows just the emails of the salespeople from the
'Southwest' region.

-----

SELECT email FROM salespeople WHERE region='Southwest';


==========
4

-----

Write a query that shows the given name, surname, and email of all
salespeople in the 'Northwest' region.

-----

SELECT givenname, surname, email FROM salespeople WHERE region='Northwest';


==========
5

-----

Write a query that shows the common name of melons that cost more than
$5.00.

-----

SELECT common_name FROM melons WHERE price > 5;


==========
6

-----

Write a query that shows the melon type and common name for all
watermelons that cost more than $5.00.


-----

SELECT melon_type, common_name FROM melons WHERE price > 5 AND melon_type = 'Watermelon';


==========
7

-----

Write a query that displays all common names of melons that start with
the letter 'C'.


-----

SELECT common_name FROM melons WHERE common_name LIKE 'C%';


==========
8

-----

Write a query that shows the common name of any melon with 'Golden'
anywhere in the common name.


-----

SELECT common_name FROM melons WHERE common_name LIKE '%Golden%';


==========
9

-----

Write a query that shows all the distinct regions that a salesperson can belong to.


-----

SELECT DISTINCT region FROM salespeople;


==========
10

-----

Write a query that shows the emails of all salespeople from both the
Northwest and Southwest regions.


-----

SELECT email FROM salespeople WHERE region='Northwest' OR region='Southwest';


==========
11

-----

Write a query that shows the emails of all salespeople from both the
Northwest and Southwest regions, this time using an 'IN' clause.  


-----

SELECT email FROM salespeople WHERE region IN ('Northwest', 'Southwest');


==========
12

-----

Write a query that shows the email, given name, and surname of all
salespeople in either the Northwest or Southwest regions whose surnames start
with the letter 'M'.

-----

SELECT email, givenname, surname FROM salespeople WHERE (region IN ('Northwest', 'Southwest') AND surname LIKE 'M%');


==========
13

-----

Write a query that shows the melon type, common name, price, and the
price of the melon given in euros. The 'melons' table has prices in dollars,
and the dollar to euro conversion rate is 0.735693.


-----

SELECT melon_type, common_name, price, price * 0.735693 FROM melons


==========
14

-----

Write a query that shows the total number of customers in our customer
table.

-----

SELECT count(*) FROM customers;


==========
15

-----

Write a query that counts the number of orders shipped to California.

-----

SELECT count(*) FROM orders WHERE shipto_state='CA';


==========
16

-----

Write a query that shows the total amount of money spent across all melon
orders.

-----

SELECT sum(order_total) FROM orders;


==========
17

-----

Write a query that shows the average order cost.

-----

SELECT AVG(order_total) FROM orders;


==========
18

-----

Write a query that shows the order total that was lowest in price.

-----

SELECT MIN(order_total) FROM orders;


==========
19

-----

Write a query that fetches the id of the customer whose email is 
'phyllis@demizz.edu'.

-----

SELECT id from customers WHERE email='phyllis@demizz.edu';


==========
20

-----

Write a query that shows the id, status and order_total for all orders 
made by customer 100.

-----

SELECT id, status, order_total FROM orders WHERE customer_id='100';


==========
21

-----

Write a single query that shows the id, status, and order total for all
orders made by 'phyllis@demizz.edu'. Use a subselect to do this.


-----

SELECT id, status, order_total FROM orders WHERE customer_id = (SELECT id FROM customers WHERE email='phyllis@demizz.edu');