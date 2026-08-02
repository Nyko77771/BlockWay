from block_app.services.ml_model_service import DomainAnalyses


analyse = DomainAnalyses()

# Check Size
print(analyse.random_forrest.feature_names_in_)
print(f'Random Forrest Size: {len(analyse.random_forrest.feature_names_in_)}')

print(f'Logistic Regression Size: {analyse.logistic_model.n_features_in_}')


# Test Analyses
print('#################')
print('Making Analyses')
analyse.create_x_features("facebook.com")
print('Logistic Model Classes: ', analyse.logistic_model.classes_)
print('Logistic Probability Score: ', analyse.logistic_probability("facebook.com"))

print('Logistic Prediction Score: ', analyse.logistic_prediction("facebook.com"))

print('LRandom Forrest Prediction Score: ',analyse.random_forrest_prediction("facebook.com"))


