from block_app.services.ml_model_service import DomainAnalyses


analyse = DomainAnalyses()

# Check Size
print(analyse.random_forrest.feature_names_in_)
print(f'Random Forrest Size: {len(analyse.random_forrest.feature_names_in_)}')

print(f'Logistic Regression Size: {analyse.logistic_model.n_features_in_}')

# Test Analyses
print(analyse.create_x_features("facebook.com"))

print(analyse.logistic_probability("facebook.com"))

print(analyse.logistic_prediction("facebook.com"))

print(analyse.random_forrest_prediction("facebook.com"))
