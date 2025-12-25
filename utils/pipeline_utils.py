# from sklearn.preprocessing import StandardScaler
# from sklearn.impute import SimpleImputer
from sklearn.base import BaseEstimator, TransformerMixin



class CustomPreprocessor(BaseEstimator, TransformerMixin):
    """Класс для препроцессинга категориальных фичей"""

    def __init__(self, cat_features=None):
        self.cat_features = cat_features

    def fit(self, X, y=None):
        if self.cat_features is None:
            self.cat_features = X.select_dtypes(include=["object", "category"]).columns
        return self

    def transform(self, X):
        X = X.copy()
        for col in self.cat_features:
            if col in X.columns:
                if X[col].dtype == "object":  # or X[col].nunique() == 2:
                    X[col] = X[col].astype("category")

                if X[col].dtype == "category":
                    X[col] = X[col].cat.add_categories("MISSING")
                    X[col] = X[col].fillna("MISSING")

        return X


# class NumPreprocessor(BaseEstimator, TransformerMixin):
#     def __init__(self, features=None, fillna=None):
#         self.features = features
#         self.scaler = StandardScaler()
#         self.imputer = SimpleImputer(strategy='median')

#     def fit(self, X, y=None):
#         if self.features is None:
#             self.features = X.select_dtypes(include=["number"]).columns

#         self.imputer.fit(X[self.features])
#         X_imp = self.imputer.transform(X[self.features])

#         self.scaler.fit(X_imp)
#         return self

#     def transform(self, X):
#         X_imp = self.imputer.transform(X)
#         return self.scaler.transform(X_imp)

#     def fit_transform(self, X):
#         return self.fit(X).transform(X)
