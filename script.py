#!/usr/bin/env python3
import json
import requests
import os
import sys
import yaml
import time
class colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"




appstartsdict = {
  'php_fpm_': 'php-fpm',
  'monitd_processes': 'monitd',
  'hdfs_datanode_': 'hdfs-datanode',
  'kube_coredns_': 'k8s-coredns',
  'squid_': 'squid',
  'memcached_': 'memcached',
  'postfix_queues_': 'postfix',
  'mongodb_': 'mongodb',
  'kvm_': 'kvm',
  'kyototycoon_': 'kyototycoon',
  'couchbase_': 'couchbase',
  'websphere.': 'websphere',
  'pgbouncer_': 'pgbouncer',
  'zookeeper_': 'zookeeper',
  'system_cpu_usage_': 'cpu-stats',
  'system_processes_': 'process',
  'powerdns_recursor_': 'powerdnsrecursor',
  'nginx_': 'nginx',
  'eventstore_': 'eventstore',
  'kube_state_': 'k8s-kube-state',
  'wildfly_': 'wildfly',
  'postgresql_': 'postgresql',
  'spark_': 'spark',
  'kube_api_': 'k8s-apiserver',
  'lighttpd_': 'lighttpd',
  'kong_': 'kong',
  'system_cpu_load_': 'cpu-load',
  'lighthouse_categories_': 'lighthouse',
  'kube_controller_': 'k8s-controller',
  'kube_kubedns_': 'k8s-kubedns',
  'redis_': 'redis',
  'riak_': 'riak',
  'crio_': 'crio',
  'activemq_': 'activemq',
  'harbor_': 'harbor',
  'oracle_': 'oracle',
  'solr_': 'solr',
  'nginx_ingress_': 'nginx-ingress-controller',
  'haproxy_': 'haproxy',
  'mysql_': 'mysql',
  'system_cpu_usage_pct': 'cpu',
  'rabbitmq_': 'rabbitmq',
  'traefik_total_count': 'traefik',
  'hdfs_namenode_': 'hdfs-namenode',
  'twemproxy_': 'twemproxy',
  'tomcat_': 'tomcat',
  'kube_metrics_': 'k8s-metrics-server',
  'openvpn_': 'openvpn',
  'system_disk_used_': 'disk',
  'jboss.': 'jboss',
  'cockroachdb_': 'cockroachdb',
  'system_uptime': 'uptime',
  'kube_': 'k8s-kubelet',
  'couchdb_': 'couchdb',
  'linkerd_': 'linkerd',
  'kube_scheduler_': 'k8s-scheduler',
  'weblogic.': 'weblogic',
  'neo4j_': 'neo4j',
  'elasticsearch_': 'elasticsearch',
  'network_interface_': 'network',
  'system_': 'memory',
  'containerd_': 'containerd',
  'hive_': 'hive',
  'kafka_': 'kafka',
  'ceph.': 'ceph',
  'etcd_': 'etcd',
  'apache_': 'apache',
  'docker_': 'docker',
  'consul_': 'consul',
  'hbase_': 'hbase',
  'varnish_': 'varnish',
  'cassandra_': 'cassandra'
}

eachpodmetric = {"docker_container_state","docker_container_size_rootfs","docker_container_size_rw","docker_cpu_usage","docker_cpu_usage_per_cpu","docker_cpu_usage_overlimit","docker_cpu_shares","docker_cpu_throttled","docker_cpu_system","docker_cpu_user","docker_io_read_bytes","docker_io_write_bytes","docker_mem_cache","docker_mem_in_use","docker_mem_usage","docker_mem_usage_overlimit","docker_mem_limit","docker_mem_mapped_file","docker_mem_pgfault","docker_mem_pgmajfault","docker_mem_pgpgin","docker_mem_pgpgout","docker_mem_active_anon","docker_mem_active_file","docker_mem_inactive_anon","docker_mem_inactive_file","docker_mem_rss","docker_mem_soft_limit","docker_mem_sw_in_use","docker_mem_sw_in_use_percent","docker_container_interface_traffic_in","docker_container_interface_traffic_out","docker_container_interface_packets_in","docker_container_interface_packets_out","docker_container_interface_errors_in","docker_container_interface_errors_out","docker_container_interface_discards_in","docker_container_interface_discards_out"}
#https://app-gi01-sjc.opsramp.net/metricsql/api/v7/tenants/client_1447633/metrics/label/__name__/values
#https://asura.opsramp.net/metricsql/api/v7/tenants/client_1447633/metrics/label/__name__/values
deltatime = 1800
starttime = int(time.time())
endtime = starttime - 18000
#endtime = 1613630494
#starttime = 1613659474
def fetch_metrics(portal_name, tenant_id, bearer_token):

    url = (
        "https://"
        + portal_name
        + ".opsramp.net/metricsql/api/v7/tenants/"
        + tenant_id
        + "/metrics/label/__name__/values"
    )

    headers = {"Authorization": "Bearer " + bearer_token, "Accept": "application/json"}
    print(url)
    try:
        return requests.get(url=url, headers=headers).json()["data"] 
    except requests.ConnectionError as ce:
        print("fetch_metrics:", ce)



def generate_metric_map():
    metric_map = dict()
    path = "metrics/"
    app_names = os.listdir(path)
    for app in app_names:
        try:
            with open(path + app + "/auto-monitoring.yaml", "r") as ymlfile:
                metrics_list = yaml.safe_load(ymlfile)
                if not isinstance(metrics_list, dict):
                    metrics_list = dict(metrics_list[0])
                metric_map[app] = set(metrics_list["metrics"])
        except OSError as err:
            print(app, err)
        except TypeError as err:
            print(app, err)
    return metric_map


def fetch_nodes(portal_name, tenant_id, bearer_token):
    url = (
        "https://"
        + portal_name
        + ".opsramp.net/metricsql/api/v7/tenants/"
        + tenant_id
        + "/metrics/label/node_name/values"
    )

    headers = {"Authorization": "Bearer " + bearer_token, "Accept": "application/json"}
    print(url)
    try:
        return requests.get(url=url, headers=headers).json()["data"]
    except requests.ConnectionError as ce:
        print("fetch_nodes:", ce)
    
def fetch_token(portal_name, client_id, client_secret):

    url = "https://" + portal_name + ".opsramp.net/auth/oauth/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        }

    body = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }

    try:
        json_response = requests.post(url=url, data=body, headers=headers)
        print(json_response.status_code)
        return json_response.json()["access_token"]
    except requests.ConnectionError as ce:
        print("fetch_token:", ce)



def fetch_metric_info(portal_name, tenant_id, bearer_token,metric_name,clustername):

    url = (
        "https://"
        + portal_name
        + ".opsramp.net/metricsql/api/v7/tenants/"
        + tenant_id
        + "/metrics?query="
        + metric_name + "%7Bcluster_name%3D%22" + clustername + "%22%7D"
        + "&end="
        + str(starttime)
        + "&start="
        + str(endtime)
        + "&step=60"
    )

    headers = {"Authorization": "Bearer " + bearer_token, "Accept": "application/json"}
    print(url)
    try:
        temp = requests.get(url=url, headers=headers).json()["data"]["result"]
        return temp
    except:
       # print("fetch_metrics:", ce)
        pass


allmetricsmap = generate_metric_map()


#sys.argv[1] - portal (eg: shivalik, Kailash etc.)
#sys.argv[2] - Client Id / Key
#sys.argv[3] - Client Secret
#sys.argv[4] - Tenant Id (eg: client_XXXXX)
#sys.argv[5] - integration_res_uuid (check the kubernetes deployment yaml for this value)
token = fetch_token(sys.argv[1],sys.argv[2],sys.argv[3])
listofmetrics = fetch_metrics(sys.argv[1], sys.argv[4], token)
for i in listofmetrics:
    print(i)
final_map = dict()
# final_map.setdefault({})
listofmetrics.sort()
print(listofmetrics)
for i in listofmetrics: 
    metric = i.split('_')
    if metric[0] in final_map.keys():
        final_map[metric[0]].add(i)
    else:
        final_map[metric[0]]= set()
        final_map[metric[0]].add(i)


t1 =  time.time()
podmetricmap = dict()
nodemetricmap = dict()
for j in listofmetrics:
    a = fetch_metric_info(sys.argv[1],sys.argv[4], token,j,sys.argv[5])
    print(j)
    #print(podmetricmap)
    #print(nodemetricmap)
    try:
      for i in a:
          podname = ""
          try:
              podname = i["metric"]["pod"]
          except KeyError as ke:
              try:
                  nodename = i["metric"]["host"]
                  if nodename in nodemetricmap.keys():
                      nodemetricmap[nodename].add(j)
                  else:
                      nodemetricmap[nodename] = set()
                      nodemetricmap[nodename].add(j)
              except KeyError as ke:
                  continue
              continue
          # try:
          #     nodename = i["metric"]["node_name"]
          # except KeyError as ke:
          #     continue
          if podname in podmetricmap.keys():
              podmetricmap[podname].add(j)
          else:
              podmetricmap[podname] = set()
              podmetricmap[podname].add(j)
    except:
      pass
t2 = time.time()
print("Total time taken in sec:", t2 - t1)
print(podmetricmap)
print(nodemetricmap)
for i in nodemetricmap:
    print("For node:",i)
    se = list(nodemetricmap[i])
    se.sort()
    print(colors.OKGREEN,se,colors.ENDC)
for i in podmetricmap:
    print("===============================================================================================")
    print("for pod:",i)
    print("Metrics Total Count:",len(eachpodmetric))
    pod_docker_metrics = podmetricmap[i].intersection(eachpodmetric)
    print("Metrics Found Count:",len(pod_docker_metrics))
    print("docker Metrics Found:",colors.OKGREEN,pod_docker_metrics,colors.ENDC)
    print("docker Metrics Not Found:",colors.FAIL,eachpodmetric - podmetricmap[i],colors.ENDC)
    rem_metrics = podmetricmap[i] - eachpodmetric
    if(len(rem_metrics)> 0):
        for j in appstartsdict:
            if list(rem_metrics)[0].startswith(j):
                appname = appstartsdict[j]
                print("Metrics found for app",appname)
                print(colors.OKGREEN,rem_metrics.intersection(allmetricsmap[appname]),colors.ENDC)
                print("Metrics Not found are")
                print(colors.FAIL,allmetricsmap[appname] - rem_metrics,colors.ENDC)


# print("====================================================================================================================")
# for i in final_map.keys():
#     # print("a")
#     try:
#         totalmetrics = allmetricsmap[i]
#     except KeyError:
#         print("found metrics are for app",i,final_map[i] - totalmetrics)

