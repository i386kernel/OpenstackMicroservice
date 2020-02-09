
from flask import Flask, request
from flask_restful import Resource, Api
from openstack import connection

app = Flask(__name__)
api = Api(app)

class WebServiceConnectionStatus(Resource):

    def get(self):
        return {"Status": "CONNECTED"}, 200

class OpenstackAuthenticator(Resource):

    conn = ""

    def post(self):
        auth_data = request.get_json()
        OpenstackAuthenticator.conn = connection.Connection(
                                                            auth_url=auth_data['auth_url'],
                                                            project_name=auth_data['project_name'],
                                                            username=auth_data['username'],
                                                            password=auth_data['password'],
                                                            user_domain_id=auth_data["user_domain_id"],
                                                            project_domain_id=auth_data["project_domain_id"]
                                                           )

class OpenstackDiscoverCluster(Resource):

    def get(self):

        '''
            Queries with OpenStack cluster and return cluster information
            :arg
                None
            :raises
                    Connection error, authentication error
            :return
                    Json object with OpenStack cluster information - return code 200
        '''

        servers = [server.name for server in OpenstackAuthenticator.conn.compute.servers()]
        networks = [network.name for network in OpenstackAuthenticator.conn.network.networks()]
        images = [image.name for image in OpenstackAuthenticator.conn.image.images()]
        flavors = [flavor.name for flavor in OpenstackAuthenticator.conn.compute.flavors()]

        openstackcluster = {"Openstack Cluster": [{"Servers": servers, "Number of Servers": len(servers)},
                                                  {"Networks": networks, "Number of Networks": len(networks)},
                                                  {"Images": images,"Number of Images": len(images)},
                                                  {"Flavors": flavors, "Number of Flavors": len(flavors)}]}

        return openstackcluster, 200 if openstackcluster else 404


class OpenstackServers(Resource):

    def get(self):

        '''
            Queries OpenStack cluster for servers and return servers.
            :arg
                None
            :raises
                   Connection error, Authentication error
            :returns
                    Json object with Server information
        '''

        comp = OpenstackAuthenticator.conn.compute.servers()
        serverslist = []
        for server in comp:
            serverslist.append(
                {
                    "Server Hostname": server.name,
                    "Server ID": server.id,
                    "Name" : server.hostname,
                    "Status" : server.status,
                    "Flavor": server.flavor,
                    "Network": server.addresses,
                }
            )
        return {"servers": serverslist}, 200 if serverslist else 404

class OpenstackNetworks(Resource):

    def get(self):

        '''
            Gets Network information from OpenStack Cluster

            :arg
                None
            :raises
                   CInternal Server Error(500), Authentication error
            :returns
                    Json Object with Network information.
        '''

        networks = OpenstackAuthenticator.conn.network.networks()
        networklist = []
        for network in networks:
            networklist.append(
                {
                    "Network Name": network.name,
                    "Network ID": network.id,
                    "Status": network.status,
                    "MTU": network.mtu,
                }
            )
        return {"networks": networklist}, 200 if networklist else 404

class OpenstackFlavors(Resource):

    def get(self):

        '''
          Gets Flavor information from OpenStack Cluster
          :arg
              None
          :raises
                 Authentication error, Internal Server Error(500)
          :returns
                  Json Object with Flavor information.
        '''

        flavors = OpenstackAuthenticator.conn.compute.flavors()
        flavorslist = []
        for flavor in flavors:
            flavorslist.append(
                        {
                            "Flavor Name": flavor.name,
                            "ID": flavor.id,
                            "Vcpus": flavor.vcpus,
                            "RAM": flavor.ram,
                            "Disk Size": f"{flavor.disk} GB",
                        }
                    )
        return {"Flavours": flavorslist}, 200 if flavorslist else 404

class OpenstackImages(Resource):

    def get(self):

        '''
          Gets Images information from OpenStack Cluster
          :arg
              None
          :raises
                 Internal Server Error(500), Authentication error
          :returns
                  Json Object with Network information.
        '''

        images = OpenstackAuthenticator.conn.image.images()
        imagelist = []
        for image in images:
            imagelist.append(
                {
                    "Image Name": image.name,
                    "Image ID": image.id,
                    "Disk Format": image.disk_format,
                    "Size": image.size,
                }
            )

        return {"Images": imagelist}, 200 if images else 404

class OpenstackCreateServer(Resource):

    def post(self):

        '''
           Creates an instance in OpenStack cluster
        :arg
            name, image_id, flavor_id, network_id
        :raises
               Internal Server Error(500), Authentication error, 401, Resource not created
        :returns
                Json Object with created server information
        '''

        data = request.get_json()
        server = OpenstackAuthenticator.conn.compute.create_server(
                                                            name=data['name'],
                                                            image_id=data['image_id'],
                                                            flavor_id=data['flavor_id'],
                                                            networks=[{'uuid': data['network_id']}]
                                                        )
        OpenstackAuthenticator.conn.wait_for_server(server, timeout=30)

        serverslist = []
        for server in OpenstackAuthenticator.conn.compute.servers():
                if server['name'] == data['name']:
                    serverslist.append(
                        {
                            "Server Hostname": server.name,
                            "Server ID": server.id,
                            "Name": server.hostname,
                            "Status": server.status,
                            "Flavor": server.flavor,
                            "Network": server.addresses,
                        }
                    )
                    return {"servers": serverslist}, 200 if serverslist else 404
        return{"Message": "Resource Not created"}, 401

class OpenstackStartServer(Resource):

    def put(self, serverID):

        '''
        Starts a stopped server, which is in Shutdown state

        :arg
          Server ID
        :raises
             Internal Server Error(500), Authentication error, 401, Resource not created
        :returns
              Json Object with started server ID.
        '''

        OpenstackAuthenticator.conn.compute.start_server(serverID)
        return {"Server Started": serverID}, 202

class OpenstackStopServer(Resource):

    def put(self, serverID):

        '''
        Shuts down a running server
        :arg
            Server ID
        :raises
               Internal Server Error(500), Authentication error, 401, Resource not created
        :returns
                Json Object with stopped server ID.
        '''

        OpenstackAuthenticator.conn.compute.stop_server(serverID)
        return {"Server Stopped": serverID}, 202

class OpenstackDeleteServer(Resource):

    def delete(self, serverID):

        '''
        Force deletes the existing server
        :arg
            Server ID
        :raises
               Internal Server Error(500), Authentication error, 401, Resource not created
        :returns
                Json Object with deleted server ID.
        '''

        OpenstackAuthenticator.conn.compute.delete_server(serverID, force=True)
        return {"Server Deleted": serverID}, 202


api.add_resource(WebServiceConnectionStatus, "/")
api.add_resource(OpenstackAuthenticator, "/auth")
api.add_resource(OpenstackDiscoverCluster, "/discovercluster")
api.add_resource(OpenstackServers, "/servers")
api.add_resource(OpenstackNetworks, "/networks")
api.add_resource(OpenstackFlavors, "/flavors")
api.add_resource(OpenstackImages, "/images")
api.add_resource(OpenstackCreateServer, "/createserver")
api.add_resource(OpenstackStopServer, "/stopserver/<string:serverID>")
api.add_resource(OpenstackStartServer, "/startserver/<string:serverID>")
api.add_resource(OpenstackDeleteServer, "/deleteserver/<string:serverID>")

if __name__ == '__main__':
    app.run(host='0.0.0.0')
