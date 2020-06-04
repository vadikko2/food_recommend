from core import Recommend


class IngredientsRecommend(Recommend):

    def find_recipe_by_tags(self, tags=[], ingredients=[], skip=0, limit=10):

        if not type(tags) is list or not type(ingredients) is list:
            assert "Error, values type should by int or list"
            return

        if not tags and not ingredients:
            recipes = self.find_by_condition("recipes", req={}, skip=skip, limit=limit)
        elif not tags and ingredients:
            recipes = self.find_by_condition("recipes", req={"ingredients.id": {"$in": ingredients}}, skip=skip, limit=limit)
        elif not ingredients and tags:
            recipes = self.find_by_condition("recipes", req={"tags": {"$in": tags}}, skip=skip, limit=limit)
        else:
            recipes = self.find_by_condition("recipes", req={
                "$and": [{"ingredients.id": {"$in": ingredients}}, {"tags": {"$in": tags}}]}, skip=skip, limit=limit)

        recommended = {"recipes": recipes, "ingredients": [], "tags": []}
        tags_set = set()
        ingredients_set = set()
        for recipe in recipes:
            ingredients_set.update([ingredient["id"] for ingredient in recipe["ingredients"]])
            tags_set.update([tag for tag in recipe["tags"]])
        recommended["ingredients"] = self.find_all_by_condition("ingredients", req={"id": {"$in": list(ingredients_set)}})
        recommended["tags"] = self.find_all_by_condition("tags", req={"id": {"$in": list(tags_set)}})

        return recommended

