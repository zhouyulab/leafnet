from tensorflow.keras.models import Model
from tensorflow.keras import layers
from repeated_module import *

def self_concatenate(layer, copies):
    layer_list = list()
    for i in range(copies):
        layer_list.append(layer)
    return layers.Concatenate()(layer_list)

def build_stoma_net_model(small_model=False, sigmoid_before_output=False):
    # Model_inputs(90,70,36)/(186,166,132)
    # (X-2)%8 = 0, OUTPUT=X-82
    # 90:8, 98:16,......186:104
    model_input = None
    if small_model:
        model_input = layers.Input(shape=(122,122,1))
    else:
        model_input = layers.Input(shape=(186,186,1))
    model_input_tower3 = layers.Cropping2D(0)(model_input)
    model_input_tower2 = layers.Cropping2D(10)(model_input)
    model_input_tower1 = layers.Cropping2D(27)(model_input)

    # define filters
    f_tower1 = 24
    f_tower2 = 12
    f_tower3 = 12
    f_concatenate = f_tower1 + f_tower2 + f_tower3
    # Towers_start
    input_tower1_concatenated = self_concatenate(model_input_tower1, f_tower1)
    input_tower2_concatenated = self_concatenate(model_input_tower2, f_tower2)
    input_tower3_concatenated = self_concatenate(model_input_tower3, f_tower3)
    # Towers_start Output
    layer_t1 = add_repeated_module_in_scale(f_tower1, 32,input_tower1_concatenated)
    layer_t2 = add_repeated_module_down_scale(f_tower2, 32,input_tower2_concatenated)
    layer_t3 = add_repeated_module_down_scale(f_tower3, 24,input_tower3_concatenated)
    # Towers_Layer1 Output = (34,34,44)/(130,82,92)
    layer_t1 = add_repeated_module_in_scale(f_tower1, 32,layer_t1)
    layer_t2 = add_repeated_module_in_scale(f_tower2, 32,layer_t2)
    layer_t3 = add_repeated_module_in_scale(f_tower3, 24,layer_t3)
    # Towers_Layer2 Output = (32,32,42)/(128,80,90)
    layer_t1 = add_repeated_module_in_scale(f_tower1, 36,layer_t1)
    layer_t2 = add_repeated_module_in_scale(f_tower2, 68,layer_t2)
    layer_t3 = add_repeated_module_down_scale(f_tower3, 52,layer_t3)
    # Towers_Layer3 Output = (30,30,20)/(126,78,44)
    layer_t1 = add_repeated_module_in_scale(f_tower1, 36,layer_t1)
    layer_t2 = add_repeated_module_down_scale(f_tower2, 68,layer_t2)
    layer_t3 = add_repeated_module_in_scale(f_tower3, 52,layer_t3)
    # Towers_Layer4 Output = (28,14,18)/(124,38,42)
    layer_t1 = add_repeated_module_in_scale(f_tower1, 36,layer_t1)
    layer_t2 = add_repeated_module_in_scale(f_tower2, 68,layer_t2)
    layer_t3 = add_repeated_module_down_scale(f_tower3, 108,layer_t3)
    # Towers_Layer5 Output = (26,12,8)/(122,36,20)
    layer_t1 = add_repeated_module_in_scale(f_tower1, 40,layer_t1)
    layer_t2 = add_repeated_module_in_scale(f_tower2, 72,layer_t2)
    layer_t3 = add_repeated_module_in_scale(f_tower3, 108,layer_t3)
    # Towers_Layer6 Output = (24,10,6)/(120,34,18)
    layer_t1 = add_repeated_module_in_scale(f_tower1, 40,layer_t1)
    layer_t2 = add_repeated_module_in_scale(f_tower2, 72,layer_t2)
    layer_t3 = add_repeated_module_in_scale(f_tower3, 108,layer_t3)
    # Towers_Layer7 Output = (22,8,4)/(18,32,16)
    layer_t1 = add_repeated_module_in_scale(f_tower1, 40,layer_t1)
    layer_t2 = add_repeated_module_in_scale(f_tower2, 72,layer_t2)
    layer_t3 = add_repeated_module_up_scale(f_tower3, 68,layer_t3)
    # Towers_Layer8 Output = (20,6,6)/(16,30,30)
    layer_t1 = add_repeated_module_in_scale(f_tower1, 44,layer_t1)
    layer_t2 = add_repeated_module_up_scale(f_tower2, 44,layer_t2)
    layer_t3 = add_repeated_module_up_scale(f_tower3, 44,layer_t3)
    # Towers_Layer9 Output = (18,10,10)/(114,58,58)
    layer_t1 = add_repeated_module_in_scale(f_tower1, 44,layer_t1)
    layer_t2 = add_repeated_module_in_scale(f_tower2, 44,layer_t2)
    layer_t3 = add_repeated_module_in_scale(f_tower3, 44,layer_t3)
    # Towers_Layer10 Output = (16,8,8)/(112,56,56)
    layer_t1 = add_repeated_module_in_scale(f_tower1, 44,layer_t1)
    layer_t2 = add_repeated_module_up_scale(f_tower2, 44,layer_t2)
    layer_t3 = add_repeated_module_up_scale(f_tower3, 44,layer_t3)
    # Towers_Layer11 Output = (14,14,14)/(110,110,110)
    layer_tc = layers.Concatenate()([layer_t1, layer_t2, layer_t3])
    # FEATURE CONCATENATION
    layer_tc = add_repeated_module_in_scale(f_concatenate, 48,layer_tc)
    # TowerC_Layer1 Output = 12/108
    layer_tc = add_repeated_module_in_scale(f_concatenate, 52,layer_tc)
    # TowerC_Layer1 Output = 10/106
    layer_tc = add_repeated_module_in_scale(f_concatenate, 56,layer_tc)
    # TowerC_Layer1 Output = 8/104
    
    if sigmoid_before_output:
        layer_tc = layers.Activation("sigmoid")(layer_tc)

    model_output = layers.Conv2D(2,1, activation='softmax')(layer_tc)
    # Softmax Output
    return Model(inputs = model_input, outputs = model_output)

a = build_stoma_net_model(True, True)