# Copyright 2021 Tier IV, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import launch
from launch.actions import DeclareLaunchArgument
from launch.actions import SetLaunchConfiguration
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
from launch.conditions import UnlessCondition
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode


def generate_launch_description():
    container = ComposableNodeContainer(
        name="mission_planning_container",
        namespace="",
        package="rclcpp_components",
        executable=LaunchConfiguration("container_executable"),
        composable_node_descriptions=[
            ComposableNode(
                package="mission_planner",
                plugin="mission_planner::MissionPlannerLanelet2",
                name="mission_planner",
                remappings=[
                    ('input/vector_map', '/map/vector_map'),
                    ('input/goal_pose', '/planning/mission_planning/goal'),
                    ('input/checkpoint', '/planning/mission_planning/checkpoint'),
                    ('output/route', '/planning/mission_planning/route'),
                    ('visualization_topic_name',
                     '/planning/mission_planning/route_marker'),
                ],
                parameters=[
                    {
                        "map_frame": "map",
                        "base_link_frame": "base_link",
                    }
                ],
                extra_arguments=[
                    {"use_intra_process_comms": LaunchConfiguration("use_intra_process")}
                ],
            ),
            ComposableNode(
                package="mission_planner",
                plugin="mission_planner::GoalPoseVisualizer",
                name="goal_pose_visualizer",
                remappings=[
                    ("input/route", "/planning/mission_planning/route"),
                    ("output/goal_pose", "/planning/mission_planning/echo_back_goal_pose"),
                ],
                extra_arguments=[
                    {"use_intra_process_comms": LaunchConfiguration("use_intra_process")}
                ],
            ),
        ],
    )

    set_container_executable = SetLaunchConfiguration(
        "container_executable",
        "component_container",
        condition=UnlessCondition(LaunchConfiguration("use_multithread")),
    )
    set_container_mt_executable = SetLaunchConfiguration(
        "container_executable",
        "component_container_mt",
        condition=IfCondition(LaunchConfiguration("use_multithread")),
    )

    return launch.LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_intra_process",
                default_value="false",
                description="use ROS2 component container communication",
            ),
            DeclareLaunchArgument(
                "use_multithread", default_value="true", description="use multithread"
            ),
            set_container_executable,
            set_container_mt_executable,
            container,
        ]
    )
