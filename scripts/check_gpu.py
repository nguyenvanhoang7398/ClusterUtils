import tensorflow as tf
config = tf.ConfigProto(
    device_count = {'GPU': 1}
)
print(tf.Session(config=config).run(tf.constant([0])))
