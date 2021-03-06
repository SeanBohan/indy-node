# Sovrin – Running the Getting Started tutorial locally

## Overview

Currently, out of the box, the [Getting Started](https://github.com/hyperledger/indy-node/blob/master/getting-started.md) tutorial uses externally running nodes and assumes that these are all up and running.  However, being test nodes, sometimes they aren’t, or sometimes you just want to see everything flowing through in a local environment.

This guide describes the process of setting up a local 4 node cluster and attaching the 3 Agents required [use the Sovrin CLI](https://github.com/hyperledger/indy-node/blob/master/getting-started.md#using-the-sovrin-cli) and impersonate Alice.

Note - I'm still trying to get my head around the details of Sovrin so there may be a few things I'm doing wrong or haven't yet understood! However this process is working nicely so far.
 

## Requirements

I’m assuming that you have Sovrin-node installed (I recommend installing this in an Ubuntu Virtual Machine if possible) – If not follow the [setup](https://github.com/hyperledger/indy-node/blob/master/setup.md) instructions.

Finally make sure that `pytest` module is installed (it is required to run test-related functionality like Faber, Acme and ThriftBank test agents): 

```
pip install pytest
```

## Initial setup
In your home folder, create a Sovrin folder. In here we are going to put the scripts we will use to setup the environment. Then change into this folder.

So first, we need to create our nodes.

Create a script ```setupEnvironment.sh``` containing:

```
# Remove .sovrin folder 
rm -rf ~/.sovrin

# Create nodes and generate initial transactions
generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 1
generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 2
generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 3
generate_sovrin_pool_transactions --nodes 4 --clients 5 --nodeNum 4

echo Environment setup complete
```

This first clears out the ~/.sovrin folder (if it exists), creates 4 nodes and then generates all the necessary initial transactions and Stewards.

Make the script executable (chmod +x setupEnvironment.sh).

At this point you are ready to build your environment.

## Start nodes

So, if you run the setupEnvironent.sh script, you should see a whole lot of output of the nodes and transactions being created.

At this point you are now ready to start the nodes.

Open up 4 new terminal windows and in each one run one of the following commands (one in each window):
```
start_sovrin_node Node1 9701 9702
start_sovrin_node Node2 9703 9704
start_sovrin_node Node3 9705 9706
start_sovrin_node Node4 9707 9708
```

This will start each node which should connect to each other, do their handshaking and will elect a master and backup.
At this point you have a nice 4 node Sovrin cluster running.

## Attach Agents to the cluster

Before we can connect the Faber, Acme and Thrift Agents to the cluster, we have to register (onboard) them with the cluster first.
To do this, we have to type the following commands using the Sovrin CLI tools started by typing ```sovrin```:

1. Add the Steward key into the Keyring to assume the Steward role. Which is a trusted entity that was created earlier as part of the generate transactions process. Its key seed has been hardcoded into the test scripts at the moment so is pre-generated:
```
new key with seed 000000000000000000000000Steward1
```
2. Connect to the cluster as this Steward to the test Sovrin cluster we are running locally:
```
connect test
```
3. Register each Agent identifier (NYM) with the Trust Anchor role which allows to on-board other identifiers:
```
send NYM dest=ULtgFQJe6bjiFbs7ke3NJD role=TRUST_ANCHOR verkey=~5kh3FB4H3NKq7tUDqeqHc1
send NYM dest=CzkavE58zgX7rUMrzSinLr role=TRUST_ANCHOR verkey=~WjXEvZ9xj4Tz9sLtzf7HVP
send NYM dest=H2aKRiDeq8aLZSydQMDbtf role=TRUST_ANCHOR verkey=~3sphzTb2itL2mwSeJ1Ji28
```
4. Impersonate each Agent owner (using pre-generated key seeds like for the Steward) and register its endpoint as an attribute against the NYM.
```
new key with seed Faber000000000000000000000000000
send ATTRIB dest=ULtgFQJe6bjiFbs7ke3NJD raw={"endpoint": {"ha": "127.0.0.1:5555", "pubkey": "5hmMA64DDQz5NzGJNVtRzNwpkZxktNQds21q3Wxxa62z"}}

new key with seed Acme0000000000000000000000000000
send ATTRIB dest=CzkavE58zgX7rUMrzSinLr raw={"endpoint": {"ha": "127.0.0.1:6666", "pubkey": "C5eqjU7NMVMGGfGfx2ubvX5H9X346bQt5qeziVAo3naQ"}}

new key with seed Thrift00000000000000000000000000
send ATTRIB dest=H2aKRiDeq8aLZSydQMDbtf raw={"endpoint": {"ha": "127.0.0.1:7777", "pubkey": "AGBjYvyM3SFnoiDGAEzkSLHvqyzVkXeMZfKDvdpEsC2x"}}
```

At this point we can start the Agents as follows, using separate sessions/windows (using [screen](https://www.gnu.org/software/screen/) for instance).

```
python /usr/lib/python3.5/site-packages/sovrin_client/test/agent/faber.py --port 5555
python /usr/lib/python3.5/site-packages/sovrin_client/test/agent/acme.py --port 6666
python /usr/lib/python3.5/site-packages/sovrin_client/test/agent/thrift.py --port 7777
```
REM: you may have to change the path to your Python interpreter and the libraries according to your environment (i. e.: ```/bin/python3.5 ~/.virtualenvs/sovrin/lib/python3.5/site-packages/sovrin_client/test/agent/...```).

Each Agent should then start up, connect to our test Sovrin cluster, handshake and be accepted as a Trust Anchor.

## Run Getting Started guide

At this point, you can follow the Getting Started guide from [Using Sovrin CLI](https://github.com/hyperledger/indy-node/blob/master/getting-started.md#using-the-sovrin-cli).
I recommend you use a seperate Sovrin CLI instance for this.

Here are the resulting commands ready to copy/paste:

```
prompt Alice
connect test

show sample/faber-invitation.sovrin
load sample/faber-invitation.sovrin
sync faber
show link faber
accept invitation from faber

show claim Transcript
request claim Transcript
show claim Transcript

show sample/acme-job-application.sovrin
load sample/acme-job-application.sovrin
sync acme
accept invitation from acme

show proof request Job-Application
set first_name to Alice
set last_name to Garcia
set phone_number to 123-45-6789
show proof request Job-Application
send proof Job-Application to Acme

show link acme

request claim Job-Certificate
show claim Job-Certificate

show sample/thrift-loan-application.sovrin
load sample/thrift-loan-application.sovrin
sync thrift
accept invitation from thrift

show proof request Loan-Application-Basic
send proof Loan-Application-Basic to Thrift Bank

show proof request Loan-Application-KYC
send proof Loan-Application-KYC to Thrift Bank
```

# Resetting the Sovrin environment

If you wish to reset your Sovrin environment and recreate it again, you can remove your ```~/.sovrin``` folder.

Then, when you want to re-create your environment from scratch, ensure that all the nodes and agents are stopped and just run the setupEnvironment.sh script.
Then you can restart the Nodes, attach the agents and away you go again.
