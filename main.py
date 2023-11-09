import random
import os
import boto3
from todoist_api_python.api import TodoistAPI

ssm_client = boto3.client('ssm', region_name='us-east-1')
api_key = ssm_client.get_parameter(Name='TODOIST_API_KEY', WithDecryption=True)
api = TodoistAPI(api_key['Parameter']['Value'])

ALL_MEALS = os.getenv('ALL_MEALS')
SHOPPING_LIST = os.getenv('SHOPPING_LIST')

try:  
    section_dict = {}
    ingredients_dict = {}

    for project in api.get_projects():
        if project.name == ALL_MEALS:
            recipe_id = project.id
        elif project.name == SHOPPING_LIST:
            shopping_id = project.id

    for section in api.get_sections():
        section_dict[str.lower(section.name)] = section.id

    for task in api.get_tasks():
        if not task.is_completed:
            if task.project_id == recipe_id:
                if not task.parent_id == None:
                    ingredient, quantity = task.content.split(": ")

                    if ingredient in ingredients_dict:
                        ingredients_dict[ingredient]["quantity"] += int(quantity)
                    else :
                        ingredients_dict[ingredient] = {"quantity": int(quantity), "label": task.labels[0]}
    
    for ingredient in ingredients_dict:
        entry = ingredients_dict[ingredient]
        content = ingredient + ": " + str(entry["quantity"])
        api.add_task(
            content=content, 
            section_id=section_dict[entry["label"]], 
            project_id=shopping_id
        )
except Exception as error:
    print(error)

