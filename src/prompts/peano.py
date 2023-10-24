PEANO_SYSTEM = """
Let's solve mathematical word problems in a careful, formal manner. The solution will follow the Peano format: 
1- Each sentence in the solution either introduces a new variable or states a new equation. 
2- The last sentence gives the goal: which variable will contain the answer to the problem. 
3- Each equation only uses previously introduced variables. 
4- Each quantity is only named by one variable.
5- Use all the numbers in the question.
""".strip()

PEANO = """
Q: Mary had 5 apples. The next morning, she ate 2 apples. Then, in the afternoon, she bought as many apples as she had after eating those apples in the morning. How many apples did she end up with?
Peano solution:
Let a be the number of apples Mary started with [[var a]]. We have [[eq a = 5]]. 
Let b be how many apples she had in the morning after eating 2 apples [[var b]]. We have [[eq b = a - 2]]. 
Let c be the apples she bought in the afternoon [[var c]]. 
Since she bought as many as she had after eating, we have [[eq c = b]]. 
Let d be how many apples she ended up with [[var d]]. We have [[eq d = b + c]]. 
The answer is the value of d [[answer d]]. 


Q: Mario and Luigi together had 10 years of experience in soccer. Luigi had 3 more than Mario. How many did Mario have?
Peano solution:
Let a be the number of years Mario had [[var a]]. 
Let b be the number of years Luigi had [[var b]]. We have [[eq a + b = 10]]. We also have [[eq b = a + 3]]. 
The answer is the value of a [[answer a]].


Q: The planet Goob completes one revolution after every 2 weeks. How many hours will it take for it to complete half a revolution?
Peano solution:
Let a be the number of hours in a week [[var a]]. We have [[eq a = 168]]. 
Let b be the number of hours in a revolution [[var b]]. We have [[eq b = a * 2]]. 
Let c be the number of hours in half a revolution [[var c]]. We have [[eq c = b / 2]]. 
The answer is the value of c [[answer c]].


Q: {question}
Peano solution:
"""




EOT0426_SYSTEM = """
You are an expert in math modeling reasoning. Please construct a mathematical model for the math word problem and write the model as a system of linear equations. Use 'x' to represent the answer. Make sure that 'x' is a number.
""".strip()


# Equation of thoughts in algebra




# linear equation system
EOT_0426 = """
Question: A deep-sea monster rises from the waters once every hundred years to feast on a ship and sate its hunger. Over three hundred years, it has consumed 847 people. Ships have been built larger over time, so each new ship has twice as many people as the last ship. How many people were on the ship the monster ate in the first hundred years?
System of linear equations:
# Assume the answer as 'x': the number of people on the ship in the first hundred years
people_ate_first_hundred_year = x
total_people_ate = 847
people_ate_second_hundred_year = 2 * people_ate_first_hundred_year
people_ate_third_hundred_year = 2 * 2 * people_ate_first_hundred_year
total_people_ate = people_ate_first_hundred_year + people_ate_second_hundred_year + people_ate_third_hundred_year


Question: Tobias is buying a new pair of shoes that costs $95. He has been saving up his money each month for the past three months. He gets a $5 allowance a month. He also mows lawns and shovels driveways. He charges $15 to mow a lawn and $7 to shovel. After buying the shoes, he has $15 in change. If he mows 4 lawns, how many driveways did he shovel?
System of linear equations:
# Assume the answer as 'x': he shovels 'x' driveways
num_shovel = x
new_shoes_cost = 95
num_months = 3
allowance_per_month = 5
lawn_charge = 15
shovel_charge = 7
money_left = 15
num_lawn = 4
new_shoes_cost + money_left = num_months * allowance_per_month + num_lawn * lawn_charge + num_shovel * shovel_charge


Question: Olivia has $23. She bought five bagels for $3 each. How much money does she have left?
System of linear equations:
# Assume the answer as 'x': Olivia has 'x' left
money_left = x
money_initial = 23
bagels = 5
bagel_cost = 3
money_spent = bagels * bagel_cost
money_left = money_initial - money_spent


Question: Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?
System of linear equations:
# Assume the answer as 'x': he has 'x' golf balls at the end of wednesday
golf_balls_end_wednesday = x
golf_balls_initial = 58
golf_balls_lost_tuesday = 23
golf_balls_lost_wednesday = 2
golf_balls_end_wednesday = golf_balls_initial - golf_balls_lost_tuesday - golf_balls_lost_wednesday


Question: {question}
System of linear equations:
"""


verbose_eot = """
Question: A deep-sea monster rises from the waters once every hundred years to feast on a ship and sate its hunger. Over three hundred years, it has consumed 847 people. Ships have been built larger over time, so each new ship has twice as many people as the last ship. How many people were on the ship the monster ate in the first hundred years?
System of linear equations:
# Assume the number of people on the ship in the first hundred years as 'x'
people_ate_first_hundred_year = x
# Over three hundred years, it has consumed 847 people
total_people_ate = 847
# Each new ship has twice as many people as the last ship
people_ate_second_hundred_year = 2 * people_ate_first_hundred_year
people_ate_third_hundred_year = 2 * people_ate_second_hundred_year
people_ate_first_hundred_year + people_ate_second_hundred_year + people_ate_third_hundred_year = total_people_ate

Question: Tobias is buying a new pair of shoes that costs $95. He has been saving up his money each month for the past three months. He gets a $5 allowance a month. He also mows lawns and shovels driveways. He charges $15 to mow a lawn and $7 to shovel. After buying the shoes, he has $15 in change. If he mows 4 lawns, how many driveways did he shovel?
System of linear equations:
# Assume he shovels 'x' driveways
num_shovel = x
# Tobias is buying a new pair of shoes that costs $95
new_shoes_cost = 95
# He has been saving up his money each month for the past three months
num_months = 3
# He gets a $5 allowance a month
allowance_per_month = 5
# He charges $15 to mow a lawn and $7 to shovel.
lawn_charge = 15
shovel_charge = 7
# he has $15 in change
money_left = 15
# he mows 4 lawns
num_lawn = 4
new_shoes_cost + money_left = num_months * allowance_per_month + num_lawn * lawn_charge + num_shovel * shovel_charge


Question: {question}:
"""
