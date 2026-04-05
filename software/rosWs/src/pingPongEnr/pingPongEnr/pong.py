'''
processes to run:
ros2 run turtlesim turtlesim_node
ros2 run pingPongEnr pong 
ros2 run turtlesim turtle_teleop_key --ros-args -r /turtle1/cmd_vel:=/player/cmd_vel

'''

import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import TeleportAbsolute
from turtlesim.srv import Kill

class pingPongEnr(Node):
    def __init__(self):
        super().__init__('pingPongEnr')
        
        self.lives = 3
        self.get_logger().info("You have 3 lives")
        self.gameOver = False
        
        #spawn turtles
        
        self.killClient = self.create_client(Kill, '/kill')
        self.killClient.wait_for_service()
        req = Kill.Request()
        req.name = 'turtle1'
        self.killClient.call_async(req)
        
        self.toSpawn = self.create_client(Spawn, '/spawn')
        self.toSpawn.wait_for_service()
        
        self.spawnTurtles() #calls spawn function
        
        
        #create publisher objects, initialize turtles
        self.pubBall = self.create_publisher(Twist,'ball/cmd_vel',10)
        self.pubPlayer = self.create_publisher(Twist,'player/cmd_vel',10)
        
        msg = Twist()
        msg.linear.x = 2.0
        msg.angular.z = 0.0
        self.pubBall.publish(msg)
        
        #create subscriptions? services? idk smth in order to get positions of turtles
        self.poseBall = None
        self.posePlayer = None
        self.cmdPlayer = None
        self.subBall = self.create_subscription(Pose,'ball/pose',self.poseBallCallback,10)
        self.subPlayer = self.create_subscription(Pose,'player/pose',self.posePlayerCallback,10)
        self.cmdSubPlayer = self.create_subscription(Twist,'player/cmd_vel',self.cmdPlayerCallback,10)
        
        #create teleport client to make bouncing off walls smoother
        self.teleportClient = self.create_client(TeleportAbsolute,'/ball/teleport_absolute')
        self.teleportClient.wait_for_service()
        
        timer_period = 0.1
        self.timer = self.create_timer(timer_period,self.gameLoop)
        
        
        
    def spawnTurtles(self):
        #Ball
        ball = Spawn.Request()
        ball.x = 5.5
        ball.y = 5.5
        ball.theta = 1.0472        
        ball.name = 'ball'
        self.toSpawn.call_async(ball)
        
        #Player
        player = Spawn.Request()
        player.x = 5.5
        player.y = 1.5
        player.theta = 0.0      
        player.name = 'player'
        self.toSpawn.call_async(player)
        
        
    
    def poseBallCallback(self,pos):
        self.poseBall = pos
        
    def posePlayerCallback(self,pos):
        self.posePlayer = pos
    
    
    def cmdPlayerCallback(self,cmd):
        self.cmdPlayer = cmd
        
        
    def gameLoop(self):
        if self.poseBall is None or self.gameOver:
            return
        
        
        y = self.poseBall.y
        x = self.poseBall.x
        t = self.poseBall.theta
        if y < 0.5:
            self.get_logger().info("Lost a Life!")
            self.lives-=1
            if self.lives == 0:
                self.gameOver = True
                self.get_logger().info("Game Over!")
            else:
                self.reset()
            return
        
        
        #Wall collision
        
        if y>10.8:
            teleReq = TeleportAbsolute.Request()
            teleReq.x = x
            teleReq.y = y #change to 10.5 if this lags
            teleReq.theta = -t
            self.teleportClient.call_async(teleReq)
            
        if x <0.2 or x>10.8:
            teleReq = TeleportAbsolute.Request()
            teleReq.x = x
            teleReq.y = y
            if t>0:
                teleReq.theta = 3.14-t
            else:
                teleReq.theta = -3.14-t
                
            self.teleportClient.call_async(teleReq)

        msg = Twist()
        msg.linear.x = 2.0
        msg.angular.z = 0.0
        self.pubBall.publish(msg)
        
        #Ball collision
        if self.posePlayer is not None:
            playerHits = abs(self.poseBall.x - self.posePlayer.x) < 0.5 and abs(self.poseBall.y - self.posePlayer.y) < 0.5
            if playerHits:
                teleReq = TeleportAbsolute.Request()
                teleReq.x = x
                teleReq.y = y
                teleReq.theta = -t
                self.teleportClient.call_async(teleReq)
        
        playerMsg = Twist()        
        playerMsg.angular.z = 0.0
        if self.cmdPlayer is not None:
            playerMsg.linear.x = self.cmdPlayer.linear.x
        else:
            playerMsg.linear.x = 0.0
            
        self.pubPlayer.publish(playerMsg)
                
    def reset(self):
        teleReq = TeleportAbsolute.Request()
        teleReq.x = 5.5
        teleReq.y = 5.5
        teleReq.theta = 0.523
        self.teleportClient.call_async(teleReq)
        
    
            
        
def main():
    rclpy.init()
    node = pingPongEnr()
    rclpy.spin(node)
    rclpy.shutdown()