import pickle as pkl


def get_w2v_kdtree_dicts(path):
    dicts = []
    for dict_file_name in ['recname2treeid.dict', "reckey2treeid.dict", "treeid2recname.dict", "treeid2reckey.dict"]:
        try:
            with open(path / dict_file_name, "rb") as dictf:
                dicts.append(pkl.load(dictf))
        except Exception as e:
            raise ValueError(f"Error while reading dict from {path / dict_file_name} file: {e}")
    return tuple(dicts)


def get_w2v_kdtree(path):
    try:
        with open(path / "w2v_kdtree.pkl", "rb") as kdtreef:
            kdtree = pkl.load(kdtreef)
    except Exception as e:
        raise ValueError(f"Error while reading kdtree from {path / 'w2v_kdtree.pkl'} file: {e}")
    return kdtree


def get_vectors(path):
    try:
        with open(path / "recipe_vectors.pkl", "rb") as vectorsf:
            vectors = pkl.load(vectorsf)
    except Exception as e:
        raise ValueError(f"Error while reading w2v vectors from {path / 'w2v_kdtree.pkl'} file: {e}")
    return vectors
