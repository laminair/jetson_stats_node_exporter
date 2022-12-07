import setuptools

setuptools.setup(
      name='jetson_stats_node_exporter',
      version='0.0.1',
      description='Prometheus Node Exporter for Nvidia Jetson Devices running Jetson Stats',
      author='HW.',
      author_email='herbert.woisetschlaeger@tum.de',
      url='https://www.cs.cit.tum.de/dis/team/herbert-woisetschlaeger/',
      package_dir={"": "jetson_stats_node_exporter"},
      packages=setuptools.find_packages("jetson_stats_node_exporter")
)