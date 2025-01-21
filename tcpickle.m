% Create a client object of the TCPickle interface
tcpickleClient = py.importlib.import_module('tcpickle_client');
client = tcpickleClient.TCPickleClient();

% Grab the data from the server
% Unfortunatly, the output of the python interface is buffered by Matlab.
% Print output is delayed until the transfer is completed...
client.initialize();
data = client.grab_data_from_server();

matlab_object = double(data);

% Plot some data
plot(matlab_object);

linkdata on

% Make it updating a few times with new data from the server
for k=1:1:100
    data = client.grab_data_from_server();
    matlab_object = double(data);
    plot(matlab_object);
    pause(0.001);
end


% Stop the server from sending more data
client.stop_server();