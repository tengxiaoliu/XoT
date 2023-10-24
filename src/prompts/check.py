ASSERT_SYSTEM = """
You are an expert in math reasoning and programming. Please check whether the final answer is correct using an assertion statement. The assertion statement is a recheck of the answer correction. You are given the question and the intermediate values of each variable. Follow the examples and complete the assertion. 
""".strip()

ASSERT_PROMPT = """
Question: Angelo and Melanie want to plan how many hours over the next week they should study together for their test next week. They have 2 chapters of their textbook to study and 4 worksheets to memorize. They figure out that they should dedicate 3 hours to each chapter of their textbook and 1.5 hours for each worksheet. If they plan to study no more than 4 hours each day, how many days should they plan to study total over the next week if they take a 10-minute break every hour, include 3 10-minute snack breaks each day, and 30 minutes for lunch each day?
chapter_hours = 6
worksheet_hours = 6
break_hours = 0.5
snack_hours = 0.5
lunch_hours = 0.5
plan_days = 4

# Assertion
# Since they plan to study no more than 4 hours each day, the total hours in plan_days should allow for all the time they need:
assert plan_days * 4 >= chapter_hours + worksheet_hours + ( break_hours + snack_hours + lunch_hours ) * plan_days



Question: Mark's basketball team scores 25 2 pointers, 8 3 pointers and 10 free throws.  Their opponents score double the 2 pointers but half the 3 pointers and free throws.  What's the total number of points scored by both teams added together?
mark_2pointers = 50
mark_3pointers = 24
mark_free_throws = 10
mark_total = 84
opponent_2pointers = 100
opponent_3pointers = 12
opponent_free_throws = 5
opponent_total = 117
total_score = 201

# Assertion
# The total number of points scores by both teams should be the summation of the total scores of two teams:
assert total_score == mark_total + opponent_total



Question: Bella has two times as many marbles as frisbees. She also has 20 more frisbees than deck cards. If she buys 2/5 times more of each item, what would be the total number of the items she will have if she currently has 60 marbles?
initial_marbles = 60
initial_frisbees = 30
initial_deck_cards = 10
initial_total = 100
after_total = 140

# Assertion
# The value of after_total is 2/5 more than the value of initial after:
assert after_total == initial_total * ( 1 + 2/5 )



Question: In a certain school, 2/3 of the male students like to play basketball, but only 1/5 of the female students like to play basketball. What percent of the population of the school do not like to play basketball if the ratio of the male to female students is 3:2 and there are 1000 students?
total_students = 1000
male = 600
female = 400
male_like_basketball = 400
female_like_basketball = 80
total_like_basketball = 480
total_dislike_basketball = 520
percent_dislike_basketball = 52

# Assertion
# The total number of students who do not like to play basketball should be the summation of (1 - 2/3) of male students and (1 - 1/5) female students:
assert total_dislike_basketball == ( 1 - 2/3 ) * male + ( 1 - 1/5 ) * female



Question: You can buy 4 apples or 1 watermelon for the same price. You bought 36 fruits evenly split between oranges, apples and watermelons, and the price of 1 orange is $0.50. How much does 1 apple cost if your total bill was $66?
each_fruit = 12
orange_cost = 6
apple_watermelon_cost = 60
watermelon_cost = 48
apple_cost = 12
per_apple_cost = 1

# Assertion
# Since you can buy 4 apples or 1 watermelon for the same price, the watermelons cost should be 4 times of the apples. The total cost of three kinds of fruits should be 66.
assert per_apple_cost * each_fruit +  per_apple_cost * 4 * each_fruit + orange_cost == 66



Question: Alyssa, Keely, and Kendall ordered 100 chicken nuggets from a fast-food restaurant. Keely and Kendall each ate twice as many as Alyssa. How many did Alyssa eat?
nuggets_total = 100
nuggets_eaten_by_alyssa = 20
nuggets_eaten_by_keely = 40
nuggets_eaten_by_kendall = 40

# Assertion
# The total number of chicken nuggets should be equal to the sum of the nuggets Keely, Kendall and Alyssa ate.
assert nuggets_total == nuggets_eaten_by_alyssa + nuggets_eaten_by_keely + nuggets_eaten_by_kendall



Question: Angela is a bike messenger in New York. She needs to deliver 8 times as many packages as meals. If she needs to deliver 27 meals and packages combined, how many meals does she deliver?
meals_and_packages = 27
meals_to_packages_ratio = 1 / 8
packages_delivered = 24
meals_delivered = 3

# Assertion
# The number of meals and packages combined should be equal to the sum of  packages delivered and meals delivered.
assert meals_and_packages == packages_delivered + meals_delivered



Question: Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more. How many golf balls did he have at the end of wednesday?
golf_balls_initial = 58
golf_balls_lost_tuesday = 23
golf_balls_lost_wednesday = 2
golf_balls_left = 33

# Assertion
# The initial golf balls should be equal to the sum of balls lost on tuesday, balls lost on wednesday and balls left.
assert golf_balls_initial == golf_balls_lost_tuesday + golf_balls_lost_wednesday + golf_balls_left



Question: {question}
{variables}

# Assertion
""".strip() + "\n"
