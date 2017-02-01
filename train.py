import array
import model
import tensorflow as tf
import csv, sys, getopt

LEARNING_RATE = 1e-4 # Need to fiddle with this to find what works well

# Get arguments for input model or output
argv = sys.argv[1:]
inputmodel = None
outputmodel = '.\model.ckpt'
try:
    opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
except getopt.GetoptError:
    print('train.py -i <inputmodel> -o <outputmodel>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('train.py -i <inputmodel> -o <outputmodel>')
        sys.exit()
    elif opt in ("-i", "--ifile"):
        inputmodel = ".\\" + arg + ".ckpt"
    elif opt in ("-o", "--ofile"):
        outputmodel = ".\\" + arg + ".ckpt"

# Start session
sess = tf.InteractiveSession()

# Learning Functions
L2NormConst = 0.001
train_vars = tf.trainable_variables()
loss = tf.reduce_mean(tf.square(tf.sub(model.y_, model.y))) + tf.add_n([tf.nn.l2_loss(v) for v in train_vars]) * L2NormConst
train_step = tf.train.AdamOptimizer(1e-4).minimize(loss)

sess.run(tf.global_variables_initializer())

# Load Model
if inputmodel is not None:
    saver = tf.train.Saver()
    saver.restore(sess, inputmodel) # Restore if model exists

# Load the csv data into memory
with open('x.csv', 'r') as csvfile:
    content = csv.reader(csvfile)
    x_data = list(content)
    
with open('y.csv', 'r') as csvfile:
    content = csv.reader(csvfile)
    y_data = list(content)
    
# Training loop variables
epochs = 100
batch_size = 50
num_samples = 24600 # Update this with more training examples
step_size = int(num_samples / batch_size)

for epoch in range(epochs):
    for i in range(step_size):

        train_step.run(feed_dict={model.x: x_data[i*batch_size : i*batch_size + batch_size], model.y_: y_data[i*batch_size : i*batch_size + batch_size], model.keep_prob: 0.8})

        if i%10 == 0:
          loss_value = loss.eval(feed_dict={model.x: x_data[i*batch_size : i*batch_size + batch_size], model.y_: y_data[i*batch_size : i*batch_size + batch_size], model.keep_prob: 1.0})
          print("epoch: %d step: %d loss: %g"%(epoch, epoch * batch_size + i, loss_value))

# Save the Model
saver = tf.train.Saver()
saver.save(sess, outputmodel)