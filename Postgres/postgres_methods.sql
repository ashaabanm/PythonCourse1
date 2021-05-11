CREATE OR REPLACE FUNCTION get_predicted_value(s_len numeric,s_w numeric,p_len numeric,p_w numeric)
    RETURNS text
    LANGUAGE 'plpython3u'
AS $BODY$
import pickle

 filename = "/home/iti/PythonTask/generated_model"

 mm = pickle.load(open(filename,'rb'))
 result = mm.predict([[s_len,s_w,p_len,p_w]])

 return result[0]
$BODY$;

-- create trigger
CREATE TRIGGER last_iris_changes
BEFORE INSERT
ON public."IRIS"
FOR EACH ROW
EXECUTE FUNCTION public.check_iris_changes();

-- create trigger function
CREATE FUNCTION check_iris_changes()
    RETURNS trigger
    LANGUAGE 'plpgsql'
AS $BODY$
DECLARE new_species text;
   BEGIN
   new_species := get_predicted_value(NEW.sepal_length,NEW.sepal_width,NEW.petal_length,NEW.petal_width);
   NEW.species := new_species;
   RETURN NEW;
   END;
$BODY$;