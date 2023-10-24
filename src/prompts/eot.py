
EOT_SYSTEM = """
Follow the examples and complete the equations for the question. Assume the value of the target answer as 'ans'. Make sure that 'ans' is a number.
""".strip()
EOT = r"""
Question: Arnel had ten boxes of pencils with the same number of pencils in each box.  He kept ten pencils and shared the remaining pencils equally with his five friends. If his friends got eight pencils each, how many pencils are in each box?

System of linear equations: (Do not simplify)


% Assume there are x pencils in each box:
pencil_per_box = x
% Arnel had ten boxes of pencils with the same number of pencils in each boxs:
total_pencil = 10 * pencil_per_box
% He kept 10 pencils:
pencil_kept = 10
% He shared the remaining pencils equally with his 5 friends, his friends got eight pencils each:
total_pencil = pencil_kept + pencil_gave
pencil_gave = 8 * 5
% How many pencils are in each box? The answer is pencil_per_box:
ans = pencil_per_box




Question: Larry spends half an hour twice a day walking and playing with his dog. He also spends a fifth of an hour every day feeding his dog. How many minutes does Larry spend on his dog each day?

System of linear equations: (Do not simplify)


% Larry spends half an hour twice a day walking and playing with his dog:
walking_time_in_hour = 1 / 2 * 2
% He also spends a fifth of an hour every day feeding his dog:
feeding_time_in_hour = 1 / 5
total_time_in_hour = walking_time_in_hour + feeding_time_in_hour
% There are 60 minutes per hour:
total_time_in_minute = total_time_in_hour * 60
% How many minutes does Larry spend on his dog each day? The answer is total_time_in_minute:
ans = total_time_in_minute




Question: Angela is a bike messenger in New York. She needs to deliver 8 times as many packages as meals. If she needs to deliver 27 meals and packages combined, how many meals does she deliver?

System of linear equations: (Do not simplify)


% Assume Angela delivers x meals:
meals = x
% She needs to deliver 8 times as many packages as meals:
packages = 8 * meals
% She needs to deliver 27 meals and packages combined:
packages + meals = 27
% How many meals does she deliver? The answer is meals:
ans = meals




Question: Last year Dallas was 3 times the age of his sister Darcy. Darcy is twice as old as Dexter who is 8 right now. How old is Dallas now?

System of linear equations: (Do not simplify)


% Assume Dallas is x years old now:
dallas = x
% Last year Dallas was 3 times the age of his sister Darcy:
dallas - 1 = 3 * (darcy - 1)
% Darcy is twice as old as Dexter:
darcy = 2 * dexter
% Dexter who is 8 right now:
dexter = 8
% How old is Dallas now?  The answer is dallas:
ans = dallas




Question: Alyssa, Keely, and Kendall ordered 100 chicken nuggets from a fast-food restaurant. Keely and Kendall each ate twice as many as Alyssa. How many did Alyssa eat?

System of linear equations: (Do not simplify)


% Assume Alyssa ate x chicken nuggets:
alyssa = x
% Alyssa, Keely, and Kendall ordered 100 chicken nuggets from a fast-food restaurant:
alyssa + keely + kendall = 100
% Keely and Kendall each ate twice as many as Alyssa:
keely = 2 * alyssa
kendall = 2 * alyssa
% How many did Alyssa eat?  The answer is alyssa:
ans = alyssa




Question: Melody planted sunflowers from two different seed packets. She found that the sunflowers from Packet A were 20% taller than the sunflowers from Packet B. If the sunflowers from Packet A were 192 inches tall, how tall were the sunflowers from Packet B?

System of linear equations: (Do not simplify)


% Assume the sunflowers from Packet B are x inches tall:
height_b = x
% The sunflowers from Packet A were 20% taller than the sunflowers from Packet B:
height_a = 1.2 * height_b
% The sunflowers from Packet A were 192 inches tall:
height_a = 192
% How tall were the sunflowers from Packet B?  The answer is height_b:
ans = height_b




Question: A deep-sea monster rises from the waters once every hundred years to feast on a ship and sate its hunger. Over three hundred years, it has consumed 847 people. Ships have been built larger over time, so each new ship has twice as many people as the last ship. How many people were on the ship the monster ate in the first hundred years?

System of linear equations: (Do not simplify)


% Over three hundred years, it has consumed 847 people:
total_people_ate = 847
% Assume the number of people on the ship in the first hundred years as x:
people_on_first_ship = x
% Each new ship has twice as many people as the last ship:
people_on_second_ship = 2 * people_on_first_ship
people_on_third_ship = 2 * people_on_second_ship
people_on_first_ship + people_on_second_ship + people_on_third_ship = total_people_ate
% How many people were on the ship the monster ate in the first hundred years?  The answer is people_on_first_ship:
ans = people_on_first_ship




Question: Tobias is buying a new pair of shoes that costs $95. He has been saving up his money each month for the past three months. He gets a $5 allowance a month. He also mows lawns and shovels driveways. He charges $15 to mow a lawn and $7 to shovel. After buying the shoes, he has $15 in change. If he mows 4 lawns, how many driveways did he shovel?

System of linear equations: (Do not simplify)


% Tobias is buying a new pair of shoes that costs $95:
shoe_cost = 95
% He has been saving up his money each month for the past three months. He gets a $5 allowance a month:
savings = 5 * 3
% He charges $15 to mow a lawn and $7 to shovel:
lawn_charge = 15
driveway_charge = 7
% After buying the shoes, he has $15 in change:
money_left = 15
% He mows 4 lawns:
lawns = 4
% Assume he shoveled x driveways:
driveways = x
shoe_cost + money_left = savings + lawns * lawn_charge + driveways * driveway_charge
% How many driveways did he shovel? The answer is driveways:
ans = driveways




Question: {question}

System of linear equations: (Do not simplify)
""".strip() + "\n\n\n"
