import random
import datetime
# import os
import boto3
from todoist_api_python.api import TodoistAPI

ssm_client = boto3.client('ssm', region_name='us-east-1')
api_key = ssm_client.get_parameter(Name='TODOIST_API_KEY', WithDecryption=True)
api = TodoistAPI(api_key['Parameter']['Value'])

# ALL_RECIPES = os.getenv('ALL_RECIPES')
# SHOPPING_LIST = os.getenv('SHOPPING_LIST')
# NUM_MEALS = os.getenv('NUM_MEALS')

ALL_RECIPES = 'Recipes'
SHOPPING_LIST = 'Shopping List'
NUM_MEALS = 1

try:  
    section_dict = {}
    ingredients_dict = {}
    recipe_id_list = []
    recipe_name_dict = {}
    all_tasks = api.get_tasks()

    for project in api.get_projects():
        if project.name == ALL_RECIPES:
            recipe_id = project.id
        elif project.name == SHOPPING_LIST:
            shopping_id = project.id

    for section in api.get_sections():
        section_dict[str.lower(section.name)] = section.id

    # Storing the relevant recipe task data
    for task in all_tasks:
        if not task.is_completed:
            if task.project_id == recipe_id:
                if task.parent_id == None:
                    recipe_id_list.append(task.id)
                    recipe_name_dict[task.id] = task.content

    # Generating random integers that would correspond with indices in recipe_id_list
    recipe_positions = [random.randint(0, len(recipe_id_list) - 1) for _ in range(0, NUM_MEALS)] # TODO: create a check to be sure that the positional number is unique
    filtered_id_list = [recipe_id_list[index] for index in recipe_positions]

    # Harmonizing ingredient type and quantity
    for task in all_tasks:
        if not task.is_completed:
            if task.parent_id in filtered_id_list:
                ingredient, quantity = task.content.split(": ")
                if ingredient in ingredients_dict:
                    ingredients_dict[ingredient]["quantity"] += int(quantity)
                else :
                    ingredients_dict[ingredient] = {"quantity": int(quantity), "label": task.labels[0]}
    
    # Creating the shopping list
    for ingredient in ingredients_dict:
        entry = ingredients_dict[ingredient]
        content = ingredient + ": " + str(entry["quantity"])
        api.add_task(
            content=content, 
            section_id=section_dict[entry["label"]], 
            project_id=shopping_id
        )
    
    # Creating the summary task in the inbox which contains the recipes for the current week
    recipe_summary_parent_id = api.add_task(content=f'Recipes for the week of {datetime.datetime.now().strftime("%m/%d/%Y")}').id

    for key in recipe_name_dict:
        if key in filtered_id_list:
            print(key)
            api.add_task(content=recipe_name_dict[key], parent_id=recipe_summary_parent_id)

except Exception as error:
    print(error)

