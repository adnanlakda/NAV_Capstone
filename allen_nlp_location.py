from allennlp.predictors.predictor import Predictor
import allennlp_models.tagging

predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/ner-elmo.2021-02-12.tar.gz")
predictor.predict(
    sentence="Did Uriah honestly think he could beat The Legend of Zelda in under three hours?."
)