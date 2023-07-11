import setuptools

setuptools.setup(
      name='jetson_stats_node_exporter',
      version='0.0.3',
      description='Prometheus Node Exporter for Nvidia Jetson Devices running Jetson Stats (now including AGX Orin)',
      author='HW.',
      author_email='herbert.woisetschlaeger@tum.de',
      url='https://www.cs.cit.tum.de/dis/team/herbert-woisetschlaeger/',
      license="GNU GPL",
      packages=["jetson_stats_node_exporter"],
      install_requires=[
            "jetson-stats==4.2.2",
            "schedule==1.0.0",
            "prometheus-client==0.15.0",
            "psutil==5.9.4",
      ],
      classifiers=[
            "License :: OSI Approved :: GNU Affero General Public License v3",
            "Programming Language :: Python :: 3",
            "Development Status :: 4 - Beta",
            "Intended Audience :: Science/Research",
            "Intended Audience :: Developers",
            "Environment :: GPU :: NVIDIA CUDA",
            "Topic :: System :: Monitoring"

      ]
)