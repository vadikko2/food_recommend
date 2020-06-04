from mainapp.core.recommendations.recommender import Recommend


class RecipeRecommend(Recommend):

    def find_recipe(self, recipe_id):
        recipe = self.find_one('recipes', req={'id': recipe_id})
        if not recipe: return None
        recommended = {"recipe": recipe, "ingredients": [], "tags": []}
        ingredients_set = set([ingredient["id"] for ingredient in recipe["ingredients"]])
        tags_set = set([tag for tag in recipe["tags"]])
        recommended["ingredients"] = self.find_all_by_condition("ingredients",
                                                                req={"id": {"$in": list(ingredients_set)}})
        recommended["tags"] = self.find_all_by_condition("tags", req={"id": {"$in": list(tags_set)}})

        return recommended
