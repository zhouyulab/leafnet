from tensorflow.keras.layers import Conv2D, Conv2DTranspose, MaxPooling2D, UpSampling2D, AveragePooling2D, Activation, BatchNormalization, concatenate, add, Cropping2D

def add_repeated_module_in_scale(f, exp_f, input_layer):
    # A modified ResNet based on the model of In Silico Labeling paper
    f = int(f)
    k = 3
    s = 1
    exp_f = int((exp_f))
    
    norm_1_layer = BatchNormalization()(input_layer)
    relu_1_layer = Activation('relu')(norm_1_layer)
    tanh_1_layer = Activation('tanh')(norm_1_layer)
    conc_1_layer = concatenate([relu_1_layer, tanh_1_layer])
    
    conv_expand = Conv2D(filters=exp_f,kernel_size=(k,k),strides=(s,s))(conc_1_layer)
    pool_1_layer = MaxPooling2D(pool_size=(k,k), strides=(s,s))(input_layer)
    conc_2_layer = concatenate([conv_expand, pool_1_layer])
    
    norm_2_layer = BatchNormalization()(conc_2_layer)
    relu_2_layer = Activation('relu')(norm_2_layer)
    tanh_2_layer = Activation('tanh')(norm_2_layer)
    conc_3_layer = concatenate([relu_2_layer, tanh_2_layer])
    
    identity_passthrough = Cropping2D(1)(input_layer)
    conv_reduce = Conv2D(filters=f,kernel_size=(1,1),strides=(1,1))(conc_3_layer)
    
    output = add([identity_passthrough, conv_reduce])
    
    return output

def add_repeated_module_down_scale(f, exp_f, input_layer):
    # A modified ResNet based on the model of In Silico Labeling paper
    f = int(f)
    k = 4
    s = 2
    exp_f = int((exp_f))
    
    norm_1_layer = BatchNormalization()(input_layer)
    relu_1_layer = Activation('relu')(norm_1_layer)
    tanh_1_layer = Activation('tanh')(norm_1_layer)
    conc_1_layer = concatenate([relu_1_layer, tanh_1_layer])
    
    conv_expand = Conv2D(filters=exp_f,kernel_size=(k,k),strides=(s,s))(conc_1_layer)
    pool_1_layer = MaxPooling2D(pool_size=(k,k), strides=(s,s))(input_layer)
    conc_2_layer = concatenate([conv_expand, pool_1_layer])
    
    norm_2_layer = BatchNormalization()(conc_2_layer)
    relu_2_layer = Activation('relu')(norm_2_layer)
    tanh_2_layer = Activation('tanh')(norm_2_layer)
    conc_3_layer = concatenate([relu_2_layer, tanh_2_layer])
    
    identity_passthrough_1 = Cropping2D(1)(input_layer)
    identity_passthrough_2 = AveragePooling2D(pool_size=(2,2), strides=(2,2))(identity_passthrough_1)
    conv_reduce = Conv2D(filters=f,kernel_size=(1,1),strides=(1,1))(conc_3_layer)
    
    output = add([identity_passthrough_2, conv_reduce])
    
    return output

def add_repeated_module_up_scale(f, exp_f, input_layer):
    # A modified ResNet based on the model of In Silico Labeling paper
    f = int(f)
    k = 4
    s = 2
    exp_f = int((exp_f))
    
    norm_1_layer = BatchNormalization()(input_layer)
    relu_1_layer = Activation('relu')(norm_1_layer)
    tanh_1_layer = Activation('tanh')(norm_1_layer)
    conc_1_layer = concatenate([relu_1_layer, tanh_1_layer])
    
    # In Up-scale config, the expand is transposed convolution, and the pooling is dropped.
    # followed by a center crop.
    conv_expand = Conv2DTranspose(filters=exp_f,kernel_size=(k,k),strides=(s,s))(conc_1_layer)
    conv_crop = Cropping2D(2)(conv_expand)

    
    norm_2_layer = BatchNormalization()(conv_crop)
    relu_2_layer = Activation('relu')(norm_2_layer)
    tanh_2_layer = Activation('tanh')(norm_2_layer)
    conc_3_layer = concatenate([relu_2_layer, tanh_2_layer])
    
    # In up_scale config, Upsampling before crop
    identity_passthrough_1 = UpSampling2D(size=(2,2))(input_layer)
    identity_passthrough_2 = Cropping2D(1)(identity_passthrough_1)
    conv_reduce = Conv2D(filters=f,kernel_size=(1,1),strides=(1,1))(conc_3_layer)
    
    output = add([identity_passthrough_2, conv_reduce])
    return output
