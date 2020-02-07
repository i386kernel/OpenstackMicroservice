from flask import Flask, request
from flask_restful import Resource, Api
from openstack import connection

app = Flask(__name__)
api = Api(app)

class OpenstackAuthenticator(Resource):
    conn = connection.Connection(
                        auth_url="http://192.168.8.250:5000/v3", 
                        project_name="admin",
                        username="admin",
                        password="c107e99096f84166",
                        user_domain_id="default",
                        project_domain_id="default"
                        )
    
class OpenstackDiscoverCluster(Resource):

    def get(self):

        '''

        Queries with OpenStack cluster and return cluster information
        Args:
            None
        Raises:
            Connection Error if Unable to connect to OpenStack cluster
        :return:
            Json object with OpenStack cluster information - return code 200

        '''

        servers = [server.name for server in OpenstackAuthenticator.conn.compute.servers()]
        networks = [network.name for network in OpenstackAuthenticator.conn.network.networks()]
        images = [image.name for image in OpenstackAuthenticator.conn.image.images()]
        flavors = [flavor.name for flavor in OpenstackAuthenticator.conn.compute.flavors()]

        openstackcluster =  {"Openstack Cluster": [{"Servers": servers, "Number of Servers": len(servers)},
                                      {"Networks": networks, "Number of Networks": len(networks)},
                                      {"Images": images,"Number of Images": len(images)},
                                      {"Flavors": flavors, "Number of Flavors": len(flavors)}]}

        return openstackcluster, 200 if openstackcluster else 404


class OpenstackServers(Resource):

    def get(self):

        '''
        
        Queries OpenStack cluster for servers and return servers.

        :arg:
            None
        :raises
            Connection error, Authentication error
        :returns:
            Json object with Server information

        '''

        comp = OpenstackAuthenticator.conn.compute.servers()
        serverslist = []
        for server in comp:
            serverslist.append(
                {
                    "Server Hostname": server.name,
                    "Name" : server.hostname,
                    "Status" : server.status,
                    "Flavor": server.flavor,
                    "Network": server.addresses,
                }
            )
        return {"servers": serverslist}

class OpenstackNetworks(Resource):

    def get(self):
        '''

        Gets Network informaiton from Openstack Cluster

        :arg
            None

        :return:


        '''
        networks = OpenstackAuthenticator.conn.network.networks()
        netlist = []
        for network in networks:
            netlist.append(
                {
                    "Network Name": network.name,
                    "Status": network.status,
                    "MTU": network.mtu,
                }
            )
        return {"networks": [network for network in networks]}

class OpenstackFlavors(Resource):
    def get(self):
        flavors = OpenstackAuthenticator.conn.compute.flavors()
        flavorslist = []
        for flavor in flavors:
            flavorslist.append(
                        {
                            "Flavor Name": flavor.name,
                            "Vcpus": flavor.vcpus,
                            "RAM": flavor.ram,
                            "ID": flavor.id,
                            "Disk Size": f"{flavor.disk} GB"
                        }
                    )
        return {"Flavours": flavorslist}

class OpenstackImages(Resource):
    def get(self):
        imagelist = []
        images = OpenstackAuthenticator.conn.image.images()
        return {"Images": [image for image in images]}

class OpenstackCreateServer(Resource):
    def post(self, name):
        data = request.get_json()
        pass
            
class OpenstackStartServer(Resource):
    def post(self, name):
        data = request.get_json()
        pass

class OpenstackStopServer(Resource):
    def post(self, name):
        data = request.get_json()
        pass

api.add_resource(OpenstackAuthenticator, "/auth")
api.add_resource(OpenstackDiscoverCluster, "/discovercluster")
api.add_resource(OpenstackServers, "/servers")
api.add_resource(OpenstackNetworks, "/networks")
api.add_resource(OpenstackFlavors, "/flavors")
api.add_resource(OpenstackImages, "/images")
api.add_resource(OpenstackCreateServer, "/CreateServer")
api.add_resource(OpenstackStopServer, "/stopserver")
api.add_resource(OpenstackStartServer, "/startserver")

if __name__ == '__main__':
    app.run(host='0.0.0.0')
