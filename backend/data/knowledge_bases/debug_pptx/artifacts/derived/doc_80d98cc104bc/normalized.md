# Robot Learning Hugging Face

[PAGE 1]

Robot Learning: A Tutorial
Francesco Capuano
 Caroline Pascal
 Adil Zouitine
 Thomas Wolf
 Michel Aractingi
University of Oxford,
 Hugging Face
Abstract
Robot learning is at an inflection point, driven by rapid advancements in machine learning and the growing
availability of large-scale robotics data. This shift from classical, model-based methods to data-driven,
learning-based paradigms is unlocking unprecedented capabilities in autonomous systems. This tutorial
navigates the landscape of modern robot learning, charting a course from the foundational principles of
Reinforcement Learning and Behavioral Cloning to generalist, language-conditioned models capable of
operating across diverse tasks and even robot embodiments. This work is intended as a guide for researchers
and practitioners, and our goal is to equip the reader with the conceptual understanding and practical tools
necessary to contribute to developments in robot learning, with ready-to-use examples implemented inlerobot.
Code:https://github.com/huggingface/lerobot
Date:October 15, 2025
Contents
1 Introduction 3
1.1LeRobotDataset. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .4
1.1.1 The dataset class design. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .4
1.2 Code Example: Batching a (Streaming) Dataset. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .5
1.3 Code Example: Collecting Data. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .6
2 Classical Robotics 9
2.1 Explicit and Implicit Models. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .9
2.2 Different Types of Motion. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .10
2.3 Example: Planar Manipulation. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .10
2.3.1 Adding Feedback Loops. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .13
2.4 Limitations of Dynamics-based Robotics. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .13
3 Robot (Reinforcement) Learning 16
3.1 A (Concise) Introduction to RL. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .17
3.2 Real-world RL for Robotics. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .20
3.2.1 Code Example: Real-world RL. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .24
3.2.2 Limitations of RL in Real-World Robotics: Simulators and Reward Design. . . . . . . . . . .32
4 Robot (Imitation) Learning 33
4.1 A (Concise) Introduction to Generative Models. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .35
4.1.1 Variational Auto-Encoders. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .36
4.1.2 Diffusion Models. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .37
4.1.3 Flow Matching. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .41
4.2 Action Chunking with Transformers. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .43
4.2.1 Code Example: Training and Using ACT in Practice. . . . . . . . . . . . . . . . . . . . . . . .46
4.3 Diffusion Policy. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .48
4.3.1 Code Example: Training and Using Diffusion Policies in Practice. . . . . . . . . . . . . . . .50
1
arXiv:2510.12403v1  [cs.RO]  14 Oct 2025

[PAGE 2]

4.4 Optimized Inference. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .52
4.4.1 Code Example: Using Async Inference. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .55
5 Generalist Robot Policies 57
5.1 Preliminaries: Models and Data. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .58
5.2 VLAs. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .60
5.2.1 VLMs for VLAs. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .60
5.3π 0 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .61
5.3.1 Code Example: Usingπ 0 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .63
5.4 SmolVLA. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .64
5.4.1 Code Example: Using SmolVLA. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .65
6 Conclusions 67
Foreword
Robotics is an inherently multidisciplinary field, which is witnessing unprecedented advancements since its inception
in the 1960s. Yet, more than sixty years after the debut of Unimate, robots have still not fully integrated into the rich,
unstructured, and dynamic world we humans inhabit. Over the decades, numerous disciplines have shown immense
promise in tackling the challenges of creating autonomous robotic systems. This tutorial takes a clear stance in the
debate on whether modern Machine Learning can play a pivotal role in the development of autonomous robots: we
believe this to be the case.
Nonetheless, we also hold that the wealth of research from both academia and industry in classical robotics over the
past six decades is, simply put, too valuable to be cast aside in favor of purely learning-based methods. However,
the interplay between classical robotics and modern machine learning is still in its nascent stages, and the path to
integration yet to be clearly defined. In turn our goal here is to present what we consider to be the most relevant
approaches within robot learning today, while warmly extending an invite to collaborate to expand the breadth of
this work! Start contributing today here.
This tutorial...
• Doesnotaim to be a comprehensive guide to general field of robotics, manipulation or underactuated systems: Si-
ciliano and Khatib (2016) and Tedrake (a,b) do this better than we ever could.
• Doesnotaim to be an introduction to statistical or deep learning: Shalev-Shwartz and Ben-David (2014) and Prince
(2023) cover these subjects better than we ever could.
• Doesnotaim to be a deep dive into Reinforcement Learning, Diffusion Models, or Flow Matching: invaluable works
such as Sutton and Barto (2018), Nakkiran et al. (2024), and Lipman et al. (2024) do this better than we ever
could.
Instead, our goal here is to provide an intuitive explanation as per why these disparate ideas have converged to form
the exciting field of modern robot learning, driving the unprecedented progress we see today. In this spirit, we follow
the adage: "a jack of all trades is a master of none,but oftentimes better than a master of one."
We sincerely hope this tutorial serves as a valuable starting point for your journey into robot learning.
2

[PAGE 3]

Figure 1 |lerobot is the open-source library for end-to-end robotics developed by Hugging Face. The library is vertically
integrated on the entire robotics stack, supporting low-level control of real-world robot devices, advanced data and inference
optimizations, as well as SOTA robot learning methods with simple implementations in pure Pytorch.
1 Introduction
Autonomous robotics holds the premise of relieving humans from repetitive, tiring or dangerous manual tasks.
Consequently, the field of robotics has been widely studied since its first inception in the 1950s. Lately, advancements
in Machine Learning (ML) have sparked the development of a relatively new class of methods used to tackle robotics
problems, leveraging large amounts of data and computation rather than human expertise and modeling skills to
develop autonomous systems.
The frontier of robotics research is indeed increasingly moving away from classical model-based control paradigm,
embracing the advancements made in ML, aiming to unlock (1) monolithic perception-to-action control pipelines
and (2) multi-modal data-driven feature extraction strategies, together with (3) reduced reliance on precise models
of the world and (4) a better positioning to benefit from the growing availability of open robotics data. While
central problems in manipulation, locomotion and whole-body control demand knowledge of rigid-body dynamics,
contact modeling, planning under uncertainty, recent results seem to indicate learning can prove just as effective as
explicit modeling, sparking interest in the field ofrobot learning. This interest can be largely justified considering the
significant challenges related to deriving accurate models of robot-environment interactions.
Moreover, since end-to-end learning on ever-growing collections of text and image data has historically been at the
core of the development offoundation modelscapable of semantic reasoning across multiple modalities (images, text,
audio, etc.), deriving robotics methods grounded in learning appears particularly consequential, especially as the
number of openly available datasets continues to grow.
Robotics is, at its core, an inherently multidisciplinary field, requiring a wide range of expertise in bothsoftwareand
hardware. The integration of learning-based techniques further broadens this spectrum of skills, raising the bar for
both research and practical applications.lerobot is an open-source library designed to integrate end-to-end with
the entire robotics stack. With a strong focus on accessible, real-world robots (1)lerobot supports many, openly
available, robotic platforms for manipulation, locomotion and even whole-body control.lerobotalso implements a
(2) unified, low-level approach to reading/writing robot configurations to extend support for other robot platforms
with relatively low effort. The library introducesLeRobotDataset, (3) a native robotics dataset’s format currently
being used by the community to efficiently record and share datasets.lerobot also supports many state-of-the-art
(SOTA) algorithms in robot learning—mainly based on Reinforcement Learning (RL) and Behavioral Cloning (BC)
techniques—with efficient implementations in Pytorch, and extended support to experimentation and experiments
tracking. Lastly, lerobot defines a custom, optimized inference stack for robotic policies decoupling action planning
from action execution, proving effective in guaranteeing more adaptability at runtime.
This tutorial serves the double purpose of providing useful references for the Science behind—and practical use
of—common robot learning techniques. To this aim, we strike to provide a rigorous yet concise overview of the core
concepts behind the techniques presented, paired with practical examples of how to use such techniques concretely,
with code examples inlerobot, for researchers and practitioners interested in the field of robot learning. This tutorial
is structured as follows:
• Section 2 reviews classical robotics foundations, introducing the limitations of dynamics-based approaches to
robotics.
3

[PAGE 4]

• Section 3 elaborates on the limitations of dynamics-based methods, and introduce RL as a practical approach to
solve robotics problems, considering its upsides and potential limitations.
• Section 4 further describes robot learning techniques that aim at solving single-tasks learning, leveraging BC
techniques to autonomously reproduce specific expert demonstrations.
• Section 5 presents recent contributions on developing generalist models for robotics applications, by learning from
large corpora of multi-task & multi-robot data (robotics foundation models).
Our goal with this tutorial is to provide an intuitive explanation of the reasons various disparate ideas from Machine
Learning (ML) have converged and are powering the current evolution of Robotics, driving the unprecedented progress
we see today. We complement our presentation of the most common and recent approaches in robot learning with
practical code implementations usinglerobot, and start here by presenting the dataset format introduced with
lerobot.
1.1LeRobotDataset
LeRobotDataset is one of the most impactful features oflerobot, developed in keeping with the observation that
robotics data is increasingly central in robot learning. Thus,lerobot defines a standardized dataset format designed to
address the specific needs of robot learning research, providing a unified and convenient access to robotics data across
modalities, including sensorimotor readings, multiple camera feeds and teleoperation status.LeRobotDataset also
accommodates for storing general information regarding the data being collected, including textual descriptions of the
task being performed by the teleoperator, the kind of robot used, and relevant measurement specifics like the frames
per second at which the recording of both image and robot state’s streams are proceeding.
In this, LeRobotDataset provides a unified interface for handling multi-modal, time-series data, and it is designed to
seamlessly integrate with the PyTorch and Hugging Face ecosystems.LeRobotDataset can be easily extended by
users and it is highly customizable by users, and it already supports openly available data coming from a variety of
embodiments supported inlerobot, ranging from manipulator platforms like the SO-100 arm and ALOHA-2 setup,
to real-world humanoid arm and hands, as well as entirely simulation-based datasets, and self-driving cars. This
dataset format is built to be both efficient for training and flexible enough to accommodate the diverse data types
encountered in robotics, while promoting reproducibility and ease of use for users.
1.1.1 The dataset class design
A core design choice behindLeRobotDataset is separating the underlying data storage from the user-facing API.
This allows for efficient storage while presenting the data in an intuitive, ready-to-use format.
Datasets are always organized into three main components:
• Tabular Data: Low-dimensional, high-frequency data such as joint states, and actions are stored in efficient memory-
mapped files, and typically offloaded to the more maturedatasets library by Hugging Face, providing fast with
limited memory consumption.
• Visual Data: To handle large volumes of camera data, frames are concatenated and encoded into MP4 files. Frames
from the same episode are always grouped together into the same video, and multiple videos are grouped together
by camera. To reduce stress on the file system, groups of videos for the same camera view are also broke into
multiple sub-directories, after a given threshold number.
• MetadataA collection of JSON files which describes the dataset’s structure in terms of its metadata, serving as the
relational counterpart to both the tabular and visual dimensions of data. Metadata include the different feature
schema, frame rates, normalization statistics, and episode boundaries.
For scalability, and to support datasets with potentially millions of trajectories (resulting in hundreds of millions
or billions of individual camera frames), we merge data from different episodes into the same high-level structure.
Concretely, this means that any given tabular collection and video will not typically contain information about one
episode only, but rather a concatenation of the information available in multiple episodes. This keeps the pressure on
the file system limited, both locally and on remote storage providers like Hugging Face, though at the expense of
leveraging more heavily relational-like, metadata parts of the dataset, which are used to reconstruct information such
as at which position, in a given file, an episode starts or ends. An example struture for a givenLeRobotDataset would
appear as follows:
•meta/info.json : This metadata is a central metadata file. It contains the complete dataset schema, defining all
4

[PAGE 5]

features (e.g., observation.state, action), their shapes, and data types. It also stores crucial information like
the dataset’s frames-per-second (fps), lerobot’s version at the time of capture, and the path templates used to
locate data and video files.
•meta/stats.json : This file stores aggregated statistics (mean, std, min, max) for each feature across the entire
dataset, used for data normalization for most policy models and accessible externally viadataset.meta.stats.
•meta/tasks.jsonl : This file contains the mapping from natural language task descriptions to integer task indices,
which are useful for task-conditioned policy training.
•meta/episodes/* This directory contains metadata about each individual episode, such as its length, the corre-
sponding task, and pointers to where its data is stored in the dataset’s files. For scalability, this information is
stored in files rather than a single large JSON file.
•data/* : Contains the core frame-by-frame tabular data, using parquet files to allow for fast, memory-mapped
access. To improve performance and handle large datasets, data from multiple episodes are concatenated into larger
files. These files are organized into chunked subdirectories to keep the size of directories manageable. A single file
typically contains data for more than one single episode.
•videos/* : Contains the MP4 video files for all visual observation streams. Similar to thedata/ directory, the
video footage from multiple episodes is concatenated into single MP4 files. This strategy significantly reduces the
number of files in the dataset, which is more efficient for modern filesystems.
1.2 Code Example: Batching a (Streaming) Dataset
This section provides an overview of how to access datasets hosted on Hugging Face using theLeRobotDataset class.
Every dataset on the Hugging Face Hub containing the three main pillars presented above (Tabular, Visual and
relational Metadata), and can be assessed with a single instruction.
In practice, most reinforcement learning (RL) and behavioral cloning (BC) algorithms tend to operate on stack of
observation and actions. For the sake of brevity, we will refer to joint spaces, and camera frames with the single term
offrame. For instance, RL algorithms may use a history of previous framesot−Ho:t to mitigate partial observability,
and BC algorithms are in practice trained to regress chunks of multiple actions (at+t+Ha) rather than single controls.
To accommodate for these specifics of robot learning training,LeRobotDataset provides a native windowing operation,
whereby users can define thesecondsof a given window (before and after) around any given frame, by using the
delta_timestemps functionality. Unavailable frames are opportunely padded, and a padding mask is also returned
to filter out the padded frames. Notably, this all happens within theLeRobotDataset, and is entirely transparent to
higher level wrappers commonly used in training ML models such astorch.utils.data.DataLoader.
Conveniently, by usingLeRobotDataset with a PytorchDataLoader one can automatically collate the individual
sample dictionaries from the dataset into a single dictionary of batched tensors for downstream training or inference.
LeRobotDataset also natively supports streaming mode for datasets. Users can stream data of a large dataset
hosted on the Hugging Face Hub, with a one-line change in their implementation. Streaming datasets supports
high-performance batch processing (ca. 80-100 it/s, varying on connectivity) and high levels of frames randomization,
key features for practical BC algorithms which otherwise may be slow or operating on highly non-i.i.d. data. This
feature is designed to improve on accessibility so that large datasets can be processed by users without requiring large
amounts of memory and storage.
Code 1: Batching a (Streaming) Dataset
https://github.com/fracapuano/robot-learning-tutorial/blob/main/snippets/ch1/01_datasets.py
1import torch
2from lerobot . da ta set s . l e r o b o t _ d a t a s e t import L e R o b o t D a t a s e t
3from lerobot . da ta set s . s t r e a m i n g _ d a t a s e t import S t r e a m i n g L e R o b o t D a t a s e t
4
5d e l t a _ t i m e s t a m p s = {
6# 0.2 , and 0.1 seconds * before * each frame
7" o b s e r v a t i o n . images . w r i s t _ c a m e r a " : [ -0.2 , -0.1 , 0.0]
8}
9
10# Optionally , use S t r e a m i n g L e R o b o t D a t a s e t to avoid d o w n l o a d i n g the dataset
11dataset = L e R o b o t D a t a s e t (
5

[PAGE 6]

12" lerobot / s v l a _ s o 1 0 1 _ p i c k p l a c e " ,
13d e l t a _ t i m e s t a m p s = d e l t a _ t i m e s t a m p s
14)
15
16# Streams frames from the Hugging Face Hub without loading into memory
17s t r e a m i n g _ d a t a s e t = S t r e a m i n g L e R o b o t D a t a s e t (
18" lerobot / s v l a _ s o 1 0 1 _ p i c k p l a c e " ,
19d e l t a _ t i m e s t a m p s = d e l t a _ t i m e s t a m p s
20)
21
22# Get the 100 th frame in the dataset by
23sample = dataset [100]
24print ( sample )
25# {
26#'o b s e r v a t i o n . state': tensor ([...]) ,
27#'action': tensor ([...]) ,
28#'o b s e r v a t i o n . images . w r i s t _ c a m e r a': tensor ([3 , C , H , W ]) , for delta t i m e s t e p s
29# ...
30# }
31
32b a t c h _ s i z e =16
33# wrap the dataset in a D a t a L o a d e r to use process it batches for tr ai ni ng p ur pos es
34d a t a _ l o a d e r = torch . utils . data . D a t a L o a d e r (
35dataset ,
36b a t c h _ s i z e = b a t c h _ s i z e
37)
38
39# Iterate over the D a t a L o a d e r in a tr ai nin g loop
40n u m _ e p o c h s = 1
41device = " cuda " if torch . cuda . i s _ a v a i l a b l e () else " cpu "
42
43for epoch in range ( n u m _ e p o c h s ):
44for batch in d a t a _ l o a d e r :
45# Move data to the a p p r o p r i a t e device ( e . g . , GPU )
46o b s e r v a t i o n s = batch [ " o b s e r v a t i o n . state " ]. to ( device )
47actions = batch [ " action " ]. to ( device )
48images = batch [ " o b s e r v a t i o n . images . w r i s t _ c a m e r a " ]. to ( device )
49
50# Next , you can do a m a z i n g _ m o d e l . forward ( batch )
51...
1.3 Code Example: Collecting Data
Code 2: Record a Dataset
https://github.com/fracapuano/robot-learning-tutorial/blob/main/snippets/ch1/02_record_data.py
1" " "
2You can also use the CLI to record data . To see the req ui re d arguments , run :
3lerobot - record -- help
4" " "
5from lerobot . cameras . opencv . c o n f i g u r a t i o n _ o p e n c v import O p e n C V C a m e r a C o n f i g
6from lerobot . da ta set s . l e r o b o t _ d a t a s e t import L e R o b o t D a t a s e t
7from lerobot . da ta set s . utils import h w _ t o _ d a t a s e t _ f e a t u r e s
8from lerobot . robots . s o 1 0 0 _ f o l l o w e r import SO100Follower , S O 1 0 0 F o l l o w e r C o n f i g
9from lerobot . t e l e o p e r a t o r s . s o 1 0 0 _ l e a d e r . c o n f i g _ s o 1 0 0 _ l e a d e r import S O 1 0 0 L e a d e r C o n f i g
10from lerobot . t e l e o p e r a t o r s . s o 1 0 0 _ l e a d e r . s o 1 0 0 _ l e a d e r import S O 1 0 0 L e a d e r
11from lerobot . utils . c o n t r o l _ u t i l s import i n i t _ k e y b o a r d _ l i s t e n e r
12from lerobot . utils . utils import log_say
13from lerobot . utils . v i s u a l i z a t i o n _ u t i l s import i n i t _ r e r u n
14from lerobot . scripts . l e r o b o t _ r e c o r d import r e c o r d _ l o o p
15
16N U M _ E P I S O D E S = 5
17FPS = 30
18E P I S O D E _ T I M E _ S E C = 60
19R E S E T _ T I M E _ S E C = 10
6

[PAGE 7]

20T A S K _ D E S C R I P T I O N = ... # provide a task d e s c r i p t i o n
21
22HF_USER = ... # provide your Hugging Face us er na me
23
24f o l l o w e r _ p o r t = ... # find your ports running : lerobot - find - port
25l e a d e r _ p o r t = ...
26f o l l o w e r _ i d = ... # to load the c a l i b r a t i o n file
27l e a d e r _ i d = ...
28
29# Create the robot and t e l e o p e r a t o r c o n f i g u r a t i o n s
30c a m e r a _ c o n f i g = { " front " : O p e n C V C a m e r a C o n f i g (
31i n d e x _ o r _ p a t h =0 , width =640 , height =480 , fps = FPS )
32}
33r o b o t _ c o n f i g = S O 1 0 0 F o l l o w e r C o n f i g (
34port = follower_port ,
35id = follower_id ,
36cameras = c a m e r a _ c o n f i g
37)
38t e l e o p _ c o n f i g = S O 1 0 0 L e a d e r C o n f i g (
39port = leader_port ,
40id = l e a d e r _ i d
41)
42
43# I n i t i a l i z e the robot and t e l e o p e r a t o r
44robot = S O 1 0 0 F o l l o w e r ( r o b o t _ c o n f i g )
45teleop = S O 1 0 0 L e a d e r ( t e l e o p _ c o n f i g )
46
47# C o n f i g u r e the dataset fe at ure s
48a c t i o n _ f e a t u r e s = h w _ t o _ d a t a s e t _ f e a t u r e s ( robot . action_features , " action " )
49o b s _ f e a t u r e s = h w _ t o _ d a t a s e t _ f e a t u r e s ( robot . o b s e r v a t i o n _ f e a t u r e s , " o b s e r v a t i o n " )
50d a t a s e t _ f e a t u r e s = {** action_features , ** o b s _ f e a t u r e s }
51
52# Create the dataset where to store the data
53dataset = L e R o b o t D a t a s e t . create (
54repo_id = f " { HF_USER }/ robot - learning - tutorial - data " ,
55fps = FPS ,
56fe at ure s = da ta se t_ fea tu re s ,
57r o b o t _ t y p e = robot . name ,
58u s e _ v i d e o s = True ,
59i m a g e _ w r i t e r _ t h r e a d s =4 ,
60)
61
62# I n i t i a l i z e the ke yb oa rd l is ten er and rerun v i s u a l i z a t i o n
63_ , events = i n i t _ k e y b o a r d _ l i s t e n e r ()
64i n i t _ r e r u n ( s e s s i o n _ n a m e = " r e c o r d i n g " )
65
66# Connect the robot and t e l e o p e r a t o r
67robot . connect ()
68teleop . connect ()
69
70e p i s o d e _ i d x = 0
71while e p i s o d e _ i d x < N U M _ E P I S O D E S and not events [ " s t o p _ r e c o r d i n g " ]:
72log_say ( f " R e c o r d i n g episode { e p i s o d e _ i d x + 1} of { N U M _ E P I S O D E S } " )
73
74r e c o r d _ l o o p (
75robot = robot ,
76events = events ,
77fps = FPS ,
78teleop = teleop ,
79dataset = dataset ,
80c o n t r o l _ t i m e _ s = EP IS OD E_T IM E_ SE C ,
81s i n g l e _ t a s k = T AS K_D ES CR IP TIO N ,
82d i s p l a y _ d a t a = True ,
83)
84
85# Reset the e n v i r o n m e n t if not s top pi ng or re - r e c o r d i n g
86if ( not events [ " s t o p _ r e c o r d i n g " ]) and \
87( e p i s o d e _ i d x < N U M _ E P I S O D E S - 1 or events [ " r e r e c o r d _ e p i s o d e " ]):
88log_say ( " Reset the e n v i r o n m e n t " )
89r e c o r d _ l o o p (
7

[PAGE 8]

90robot = robot ,
91events = events ,
92fps = FPS ,
93teleop = teleop ,
94c o n t r o l _ t i m e _ s = RESET_TIME_SEC ,
95s i n g l e _ t a s k = TAS K_ DE SC RIP TI ON ,
96d i s p l a y _ d a t a = True ,
97)
98
99if events [ " r e r e c o r d _ e p i s o d e " ]:
100log_say ( " Re - r e c o r d i n g episode " )
101events [ " r e r e c o r d _ e p i s o d e " ] = False
102events [ " e x i t _ e a r l y " ] = False
103dataset . c l e a r _ e p i s o d e _ b u f f e r ()
104c ont in ue
105
106dataset . s a v e _ e p i s o d e ()
107e p i s o d e _ i d x += 1
108
109# Clean up
110log_say ( " Stop r e c o r d i n g " )
111robot . d i s c o n n e c t ()
112teleop . d i s c o n n e c t ()
113dataset . p u s h _ t o _ h u b ()
8

[PAGE 9]

Figure 2|Overview of methods to generate motion (clearly non-exhausitve, see Bekris et al. (2024)). The different methods
can be grouped based on whether they explicitly (dynamics-based) or implicitly (learning-based) model robot-environment
interactions.
2 Classical Robotics
Know your enemy[...]
Sun Tzu
TL;DR
Learning-based approaches to robotics are motivated by the need to (1) generalize across tasks and embodiments
(2) reduce dependency on human expertise (3) leverage historical trends on the production of data—all
traditionally overlooked by dynamics-based techniques.
2.1 Explicit and Implicit Models
Robotics is concerned with producing artificial motion in the physical world in useful, reliable and safe fashion. Thus,
robotics is an inherently multi-disciplinar domain: producing autonomous motion in the physical world requires, to the
very least, interfacing different software (motion planners) and hardware (motion executioners) components. Further,
knowledge of mechanical, electrical, and software engineering, as well as rigid-body mechanics and control theory
have therefore proven quintessential in robotics since the field first developed in the 1950s. More recently, Machine
Learning (ML) has also proved effective in robotics, complementing these more traditional disciplines (Connell and
Mahadevan, 1993). As a direct consequence of its multi-disciplinar nature, robotics has developed as a rather wide
array of methods, all concerned with the main purpose of producing artificial motion in the physical world.
Methods to produce robotics motion range from traditionalexplicitmodels—dynamics-based1 methods, leveraging
precise descriptions of the mechanics of robots’ rigid bodies and their interactions with eventual obstacles in the
environment—toimplicitmodels—learning-based methods, treating artificial motion as a statistical pattern to learn
given multiple sensorimotor readings (Agrawal; Bekris et al., 2024). A variety of methods have been developed
between these two extrema. For instance, Hansen et al. (2022) show how learning-based systems can benefit from
information on the physics of problems, complementing a traditional learning method such as Temporal Difference
(TD)-learning Sutton and Barto (2018) with Model-Predictive Control (MPC). Conversely, as explicit models may
be relying on assumptions proving overly simplistic—or even unrealistic—in practice, learning can prove effective
to improve modeling of complex phenomena or complement perception (McCormac et al., 2016). Such examples
1In here, we refer to bothkinematicsanddynamics-based control.
9

[PAGE 10]

Figure 3 | Different kinds of motions are achieved with potentially very different robotic platforms. From left to right, top to
bottom: ViperX, SO-100, Boston Dynamics’ Spot, Open-Duck, 1X’s NEO, Boston Dynamics’ Atlas. This is an example list of
robotic platforms and is (very) far from being exhaustive.
aim at demonstrating the richness of approaches to robotics, and Figure 2 graphically illustrates some of the most
relevant techniques. Such a list is clearly far from being exhaustive, and we refer to Bekris et al. (2024) for a more
comprehensive overview of both general and application-specific methods for motion generation. In this section, we
wish to introduce the inherent benefits of learning-based approaches to robotics—the core focus on this tutorial.
2.2 Different Types of Motion
In the vast majority of instances, robotics deals with producing motion via actuating joints connecting nearly
entirely-rigid links. A key distinction between focus areas in robotics is based on whether the generated motion
modifies (1) the absolute state of the environment (via dexterity), (2) the relative state of the robot with respect to
its environment (exercising mobility skills), or (3) a combination of the two (Figure 3).
Effects such as (1) are typically achievedthroughthe robot, i.e. generating motion to perform an action inducing
a desirable modification, effectivelymanipulatingthe environment (manipulation). Motions like (2) may result in
changes in the robot’s physical location within its environment. Generally, modifications to a robot’s location within
its environment may be considered instances of the generallocomotionproblem, further specified aswheeledorlegged
locomotion based on whenever a robot makes use of wheels or leg(s) to move in the environment. Lastly, an increased
level of dynamism in the robot-environment interactions can be obtained combining (1) and (2), thus designing
systems capable to interact withandmove within their environment. This category is problems is typically termed
mobile manipulation, and is characterized by a typically much larger set of control variables compared to either
locomotion or manipulation alone.
The traditional body of work developed since the very inception of robotics is increasingly complemented by learning-
based approaches. ML has indeed proven particularly transformative across the entire robotics stack, first empowering
planning-based techniques with improved state estimation used for traditional planning (Tang et al., 2023) and
then end-to-end replacing controllers, effectively yielding perception-to-action methods (Kober et al.). Work in
producing robots capable of navigating a diverse set of terrains demonstrated the premise of both dynamics and
learning-based approaches for locomotion (Griffin et al., 2017; Ji et al., 2023; Lee et al., 2020; Margolis et al., 2022),
and recent works on whole-body control indicated the premise of learning-based approaches to generate rich motion
on complex robots, including humanoids (Zhang et al., 2024; Bjorck et al., 2025). Manipulation has also been widely
studied, particularly considering its relevance for many impactful use-cases ranging from high-risk applications for
humans (Fujita et al., 2020; Alizadeh and Zhu, 2024) to manufacturing (Sanneman et al., 2020). While explicit models
have proven fundamental in achieving important milestones towards the development of modern robotics, recent
works leveraging implicit models proved particularly promising in surpassing scalability and applicability challenges
via learning (Kober et al.).
2.3 Example: Planar Manipulation
Robot manipulators typically consist of a series of links and joints, articulated in a chain finally connected to an
end-effector. Actuated joints are considered responsible for generating motion of the links, while the end effector is
instead used to perform specific actions at the target location (e.g., grasping/releasing objects via closing/opening a
gripper end-effector, using a specialized tool like a screwdriver, etc.).
10

[PAGE 11]

Figure 4 | Cheaper, more accessible robots are starting to rival traditional platforms like the Panda arm platforms in adoption
in resource-constrained scenarios. The SO-100, in particular, has a cost in the 100s of Euros, and can be entirely 3D-printed in
hours, while the industrially-manufactured Panda arm costs tens of thousands of Euros and is not openly available.
Figure 5 | The SO-100 arm is a 6-dof manipulator arm. Preventing some of its joints (shoulder pane, wrist flex and wrist roll)
from actuating, it can be represented as a traditional 2-dof planar manipulator (the gripper joint in the end-effector is not
considered towards the count of the degrees of freedom used to produce motion).
Recently, the development of low-cost manipulators like the ALOHA (Zhao et al., 2023) ALOHA-2 (Aldaco et al.)
and SO-100/SO-101 (Knight et al.) platforms significantly lowered the barrier to entry to robotics, considering the
increased accessibility of these robots compared to more traditional platforms like the Franka Emika Panda arm
(Figure 4).
Deriving an intuition as per why learning-based approaches are gaining popularity in the robotics community requires
briefly analyzing traditional approaches for manipulation, leveraging tools like forward and inverse kinematics (FK,
IK) and control theory. Providing a detailed overview of these methods falls (well) out of the scope of this tutorial,
and we refer the reader to works including Siciliano and Khatib (2016); Lynch and Park (2017); Tedrake (a,b) for a
much more comprehensive description of these techniques. Here, we mostly wish to highlight the benefits of ML over
these traditional techniques
Consider the (simple) case where a SO-100 is restrained from actuating (1) the shoulder pane and (2) the wrist flex
and roll motors. This effectively reduces the degrees of freedom of the SO-100 from the original 5+1 (5 joints + 1
gripper) to 2+1 (shoulder lift, elbow flex + gripper). As the end-effector does not impact motion in this model,
the SO-100 is effectively reduced to the planar manipulator robot presented in Figure 5, where spheres represent
actuators, and solid lines indicate length-llinks from the base of the SO-100 to the end-effector (ee).
Further, let us make the simplifying assumption that actuators can produce rotations up to2πradians. In practice,
this is seldom the case due to movement obstructions caused by the robot body itself (for instance, the shoulder lift
cannot produce counter-clockwise movement due to the presence of the robot’s base used to secure the SO-100 to its
support and host the robot bus), but we will introduce movement obstruction at a later stage.
All these simplifying assumptions leave us with the planar manipulator of Figure 6a, free of moving its end-
effector by controlling the anglesθ1 and θ2, jointly referred to as the robot’sconfiguration, and indicated with
q = [θ1,θ 2]∈ [−π, +π]2. The axis attached to the joints indicate the associated reference frame, whereas circular
11

[PAGE 12]

(a)|Free to move
 (b)|Constrained by the surface
 (c) | Constrained by surface and (fixed)
obstacle
Figure 6 | Planar, 2-dof schematic representation of the SO-100 manipulator under diverse deployment settings. From left
to right: completely free of moving; constrained by the presence of the surface; constrained by the surface and presence of
obstacles. Circular arrows around each joint indicate the maximal rotation feasible at that joint.
arrows indicate the maximal feasible rotation allowed at each joint. In this tutorial, we do not cover topics related to
spatial algebra, and we instead refer the reader to Lynch and Park (2017, Chapter 2) and Tedrake (a, Chapter 3) for
excellent explanations of the mechanics and theoretical foundations of producing motion on rigid bodies.
Considering the (toy) example presented in Figure 6a, then we can analytically write the end-effector’s positionp∈R 2
as a function of the robot’s configuration,p=p(q),p:Q7→R 2. In particular, we have:
p(q) =
 
px(θ1,θ 2)
py(θ1,θ 2)
!
=
 
lcos(θ 1) +lcos(θ 1 +θ 2)
lsin(θ 1) +lsin(θ 1 +θ 2)
!
∈S n=2
l1+l2 ={p(q)∈R 2 :∥p(q)∥ 2
2≤(2l) 2,∀q∈Q}
Deriving the end-effector’spose—positionandorientation—in some m-dimensional space p∈P⊂R m starting from
the configurationq∈Q⊂R n of an-joints robot is referred to asforward kinematics(FK), whereas identifying the
configuration corresponding to any given target pose is termedinverse kinematics(IK). In that, FK is used to map a
robot configuration into the corresponding end-effector pose, whereas IK is used to reconstruct the configuration(s)
given an end-effector pose.
In the simplified case here considered (for whichp≡p , as the orientation of the end-effector is disregarded for
simplicity), one can solve the problem of controlling the end-effector’s location to reach a goal positionp∗ by solving
analytically forq :p(q) =fFK(q) =p∗. However, in the general case, one might not be able to solve this problem
analytically, and can typically resort to iterative optimization methods comparing candidate solutions using a loss
function (in the simplest case,∥p(q)−p∗∥2
2 is a natural candidate), yielding:
min
q∈Q
∥p(q)−p ∗∥2
2.(1)
Exact analytical solutions to IK are even less appealing when one considers the presence of obstacles in the robot’s
workspace, resulting in constraints on the possible values ofq∈Q⊆ [−π, +π]n⊂R n in the general case ofn-links
robots.
For instance, the robot in Figure 6b is (very naturally) obstacled by the presence of the surface upon which it rests:θ1
can now exclusively vary within[0,π ], while possible variations inθ2 depend onθ1 (when θ1→ 0or θ1→π , further
downwards movements are restricted). Even for a simplified kinematic model, developing techniques to solve eq. 1 is
in general non-trivial in the presence of constraints, particularly considering that the feasible set of solutionsQ may
change across problems. Figure 6c provides an example of how the environment influences the feasible set considered,
with a new set of constraints deriving from the position of a new obstacle.
However, IK—solving eq. 1 for a feasibleq—only proves useful in determining information regarding the robot’s
configuration in the goal pose, and crucially does not provide information on thetrajectoryto follow over time to
reach a target pose. Expert-defined trajectories obviate to this problem providing a length-K succession of goal
poses τK = [p∗
0,p∗
1,...p ∗
K]for tracking. In practice, trajectories can also be obtained automatically throughmotion
planningalgorithms, thus avoiding expensive trajectory definition from human experts. However, trackingτK via
IK can prove prohibitively expensive, as tracking would requireK resolutions of eq. 1 (one for each target pose).
Differentialinverse kinematics (diff-IK) complements IK via closed-form solution of a variant of eq. 1. LetJ(q)denote
12

[PAGE 13]

the Jacobian matrix of (partial) derivatives of the FK-functionfFK :Q7→P , such thatJ(q) = ∂fFK (q)
∂q . Then, one
can apply the chain rule to anyp(q) =fFK(q), deriving ˙p=J(q) ˙q, and thus finally relating variations in the robot
configurations to variations in pose, thereby providing a platform for control.
Given a desired end-effector trajectory˙p∗(t)(1) indicating anchor regions in space and (2) how much time to spend
in each region, diff-IK finds˙q(t)solving for joints’velocitiesinstead ofconfigurations,
˙q(t) = arg min
ν
∥J(q(t))ν−˙p∗(t)∥2
2 (2)
Unlike eq. 1, solving for˙qis much less dependent on the environment (typically, variations in velocity are constrained
by physical limits on the actuators). Conveniently, eq. 2 also often admits the closed-form solution˙q= J(q)+ ˙p∗,
where J+(q)denotes the Moore-Penrose pseudo-inverse ofJ(q). Finally, discrete-time joint configurationsq can be
reconstructed from joint velocities˙qusing forward-integration on the continuous-time joint velocity ,qt+1 =qt + ∆t˙qt
for a given∆t, resulting in tracking via diff-IK.
Following trajectories with diff-IK is a valid option in well-controlled and static environments (e.g., industrial
manipulators in controlled manufacturing settings), and relies on the ability to define a set of target velocities to
track[ ˙p∗
0,˙p∗
1,...,˙p ∗
k]—an error-prone task largely requiring human expertise. Furthermore, diff-IK relies on the ability
to (1) accessJ(q)∀q∈Q and (2) compute its pseudo-inverse at every iteration of a given control cycle—a challenging
assumption in highly dynamical settings, or for complex kinematic chains.
2.3.1 Adding Feedback Loops
While very effective when a goal trajectory has been well specified, the performance of diff-IK can degrade significantly
in the presence of modeling/tracking errors, or in the presence of non-modeled dynamics in the environment.
Figure 7 | Planar manipulator robot
in the presence of a moving obstacle.
One such case is presented in Figure 7, where another rigid body other than
the manipulator is moving in the environment along the horizontal axis, with
velocity ˙xB. Accounting analytically for the presence of this disturbance—for
instance, to prevent the midpoint of the link from ever colliding with the
object—requires access to ˙xB at least, to derive the equation characterizing
the motion of the environment.
Less predictable disturbances however (e.g.,˙xB←˙xB +ε,ε∼N (0, 1)) may
prove challenging to model analytically, and one could attain the same result of
preventing link-object collision by adding a condition on the distance between
the midpoint ofl and xB, enforced through a feedback loop on the position
of the robot and object at each control cycle.
To mitigate the effect of modeling errors, sensing noise and other disturbances,
classical pipelines indeed do augment diff-IK with feedback control looping back quantities of interest. In practice,
following a trajectory with a closed feedback loop might consist in backwarding the error between the target and
measured pose,∆p =p∗−p (q), hereby modifying the control applied to˙q=J(q)+( ˙p∗ +kp∆p), withkp defined as
the (proportional) gain.
More advanced techniques for control consisting in feedback linearization, PID control, Linear Quatratic Regulator
(LQR) or Model-Predictive Control (MPC) can be employed to stabilize tracking and reject moderate perturbations,
and we refer to Siciliano and Khatib (2016, Chapter 8) for in-detail explanation of these concepts, or (Tedrake, a,
Chapter 8) for a simple, intuitive example in the case of a point-mass system. Nonetheless, feedback control presents
its challenges as well: tuning gains remains laborious and system-specific. Further, manipulation tasks present
intermittent contacts inducing hybrid dynamics (mode switches) and discontinuities in the Jacobian, challenging
the stability guarantees of the controller and thus often necessitating rather conservative gains and substantial
hand-tuning.
We point the interested reader to Siciliano and Khatib (2016, Chapter 2,7,8), Lynch and Park (2017, Chapter 6,11),
and Tedrake (a, Chapter 3,8) for extended coverage of FK, IK, diff-IK and control for (diff-)IK.
2.4 Limitations of Dynamics-based Robotics
Despite the last 60+ years of robotics research, autonomous robots are still largely incapable of performing tasks at
human-level performance in the physical world generalizing across (1) robot embodiments (different manipulators,
13

[PAGE 14]

Figure 8 | Dynamics-based approaches to robotics suffer from several limitations: (1) orchestrating multiple components poses
integration challenges; (2) the need to develop custom processing pipelines for the sensing modalities and tasks considered
hinders scalability; (3) simplified analytical models of physical phenomena (here friction at the gripper; credits to Antonova
et al. (2017)) limit real-world performance. Lastly, (4) dynamics-based methods overlook trends in the availability and growth
of robotics data.
different locomotion platforms, etc.) and (2) tasks (tying shoe-laces, manipulating a diverse set of objects). While
essential in the early development of robotics, the aforementioned methods require significant human expertise to be
used in practice, and are typically specific to a particular applicative problem.
Dynamics-based robotics pipelines have historically been developed sequentially, engineering the different blocks now
within most architectures for specific purposes. That is, sensing, state estimation, mapping, planning, (diff-)IK, and
low-level control have been traditionally developed as distinct modules with fixed interfaces. Pipelining these specific
modules proved error-prone, and brittleness emerges—alongside compounding errors—whenever changes incur (e.g.,
changes in lighting for sensing, occlusion/failure of sensors, control failures). Adapting such a stack to new tasks
or robotic platforms often entails re-specifying objectives, constraints, and heuristics at multiple stages, incurring
significant engineering overhead.
Moreover, classical planners operate on compact, assumed-sufficient state representations; extending them to reason
directly over raw, heterogeneous and noisy data streams is non-trivial. This results in a limited scalability to
multimodal data and multitask settings, as incorporating high-dimensional perceptual inputs (RGB, depth, tactile,
audio) traditionally required extensive engineering efforts to extract meaningful features for control. Also, the large
number of tasks, coupled with the adoption ofper-taskplanners, goal parameterizations, and safety constraints,
results in an explosion in design and validation options, with little opportunity to reuse solutions across tasks.
Setting aside integration and scalability challenges: developing accurate modeling of contact, friction, and compliance
for complicated systems remains difficult. Rigid-body approximations are often insufficient in the presence of
deformable objects, and relying on approximated models hinders real-world applicability of the methods developed.
14

[PAGE 15]

In the case of complex, time-dependent and/or non-linear dynamics, even moderate mismatches in parameters,
unmodeled evolutions, or grasp-induced couplings can qualitatively affect the observed dynamics.
Lastly, dynamics-based methods (naturally) overlook the rather recent increase in availability of openly-available
robotics datasets. The curation of academic datasets by large centralized groups of human experts in robotics (O’Neill
et al., 2025; Khazatsky et al., 2025) is now increasingly complemented by a growing number of robotics datasets
contributed in a decentralized fashion by individuals with varied expertise. If not tangentially, dynamics-based
approaches are not posed to maximally benefit from this trend, which holds the premise of allowing generalization in
the space of tasks and embodiments, like data was the cornerstone for advancements in vision (Alayrac et al., 2022)
and natural-language understanding (Brown et al., 2020).
Taken together, these limitations (Figure 8) motivate the exploration of learning-based approaches that can (1)
integrate perception and control more tightly, (2) adapt across tasks and embodiments with reduced expert modeling
interventions and (3) scale gracefully in performance as more robotics data becomes available.
15

[PAGE 16]

Figure 9 | Learning-based robotics streamlines perception-to-action by learning a (1) unified high-level controller capable to
take (2) high-dimensional, unstructured sensorimotor information. Learning (3) does not require a dynamics model and instead
focuses on interaction data, and (4) empirically correlates with the scale of the data used.
3 Robot (Reinforcement) Learning
Approximate the solution, not the
problem[...]
Richard Sutton
TL;DR
The need for expensive, high-fidelity simulators can be obviated learning from real-world data, using sample-
efficient algorithms that can safely train directly on hardware.
Learning-based techniques for robotics naturally address the limitations presented in Section 2 (Figure 9). In particular,
learning-based techniques typically rely on monolithich prediction-to-action pipelines (visuomotor policies) which
do directly map sensorimotor inputs to predicted actions, streamlining control policies by removing the need to
interface multiple components. Mapping sensory inputs to actions also makes it possible to incorporate diverse
input modalities, leveraging the automatic feature extraction capabilities of modern learning systems. Moreover,
learning-based approaches can, in principle, bypass explicit modeling altogether and instead rely solely on interaction
data—an advantage that proves transformative when dynamics are difficult to model or entirely unknown. Lastly,
learning for robotics (robot learning) is naturally well posed to leverage the growing amount of robotics data openly
available, just as computer vision and natural language processing did historically benefit from large-scale corpora of
data, in great part overlooked by dynamics-based approaches.
Being a field at its relative nascent stages, no prevalent technique(s) proves distinctly better than any other in the
16

[PAGE 17]

Figure 11 | Examples of two different robotics tasks performed using RL. In the manipulation task (A) an agent learns to reach
for a yellow plastic block in its environment, and to put it inside of a box. In the locomotion task (B) an agent learns to move
its center of mass sideways without falling.
domain of robot learning. Still, two major classes of methods gained prominence: Reinforcement Learning (RL) and
Behavioral Cloning (BC) (Figure 10). In this section, we provide a conceptual overview of applications of RL to
robotics, as well as introduce practical examples of how to use RL withinlerobot. We then introduce the major
limitations RL suffers from, to introduce BC techniques in Section 4 and Section sec:learning-foundation.
Figure 10 | Overview of the
robot learning methods implemented
in lerobot. All algorithms are imple-
mented in Pytorch. References: Zhao
etal.(2023);Chietal.(2024);Leeetal.
(2024); Black et al. (2024); Shukor et al.
(2025); Luo et al. (2024); Hansen et al.
(2022) (top-to-bottom, left-to-right).
In Figure 10 we deliberately include generalist robot models (Black et al.,
2024; Shukor et al., 2025) alongside task-specific BC methods. While signif-
icantly different in spirit—generalistmodels are language-conditioned and use
instructions to generate motion valid across many tasks, whiletask-specific
models are typically not language-conditioned and used to perform a single
task—foundationmodels are still largely trained to reproduce trajectories
contained in a (large) training set of input demonstrations. Thus, we argue
generalist policies can indeed be grouped alongside other task-specific BC
methods, as they both leverage similar training data and schemas. Figure 10 il-
lustrates this categorization graphically, explicitly listing all the robot learning
policies currently available inlerobot: Action Chunking with Transformers
(ACT) (Zhao et al., 2023), Diffusion Policy (Chi et al., 2024), Vector-Quantized
Behavior Transformer (VQ-BeT) (Lee et al., 2024),π0 (Black et al., 2024),
SmolVLA (Shukor et al., 2025), Human-in-the-loop Sample-efficient RL (HIL-
SERL) (Luo et al., 2024) and TD-MPC (Hansen et al., 2022).
Applications of RL to robotics have been studied long enough that the rela-
tionship between these two disciplines has been compared to that of physics
and matematics (Kober et al.). Indeed, due to their inherently interactive
and sequential nature, robotics control problems can be directly cast as RL
problems. Figure 11 presents two of such cases. Reaching for an object to
then move it somewhere else in the scene is a sequential problem where over
time the controller needs to adjust the position of the robot arm based on
the current configuration and the (possibly varying) position of the object.
Figure 11 also shows an example of a locomotion problem, where sequentiality is inherent in the problem formulation:
while sliding to the side, the controller needs to keep adjusting to the robot’s to avoid failure (falling).
3.1 A (Concise) Introduction to RL
The RL framework (Sutton and Barto, 2018), which we briefly introduce here, has often been used to tackle robotics
problems (Kober et al.). RL is a subfield within ML fundamentally concerned with the development of autonomous
systems (agents) capable tocontinuously behavein an evolving environment, developing (ideally, well-performing)
control strategies (policies). Crucially for robotics, RL agents improve through trial and error, bypassing explicit
models of the problem dynamics in favor of interaction data. In RL, this feedback loop between actions and outcomes
(Figure 12) is established through the agent sensing a scalar quantity (reward) measuring how desirable a given
transitionis for the accomplishment of its goal.
Formally, interactions between an agent and its environment are typically modeled via a Markov Decision Pro-
17

[PAGE 18]

Figure 12|Agent-Environment interaction diagram (image credits to Sutton and Barto (2018)).
cess (MDP) (Bellman, 1957). Representing robotics problems via MDPs offers several advantages, including (1)
incorporating uncertainty through MDP’s inherently stochastic formulation and (2) providing a theoretically-sound
framework for learningwithoutan explicit model of the environment dynamics. While accommodating a continuous
time formulation too, MDPs are typically considered in discrete time in RL, assuming interactions to atomically take
place at discretetimestep t = 0, 1, 2, 3,...,T . MDPs allowing for an unbounded number of interactions (T→ +∞)
are termedinfinite-horizon, and opposed tofinite-horizonMDPs in which T is finite. Unless diversely specified, we
will only be referring to discrete-time finite-horizon (episodic) MDPs.
Formally, a lenght-TMarkov Decision Process (MDP) is a tupleM=⟨S,A,D,r,γ,ρ,T⟩, where:
•S is thestate space; st∈S denotes the (possibly non-directly observable) environment state at timet. In robotics,
states often comprise robot configuration and velocities (qt,˙qt), and can also accomodate sensor readings such as
camera or audio streams.
•A is theaction space; at∈A may represent joint torques, joint velocities, or even end-effector commands at
timestept. In general, actions correspond to commands intervenings on the configuration of the robot.
•D represents the (possibly non-deterministic) environment dynamics, withD :S×A×S7→ [0, 1],D (st,at,st+1) =
P(st+1|st,at). For instance, for a planar manipulator dynamics could be considered deterministic when the
environment is fully described (Figure 6a), and stochastic when unmodeled disturbances depending on non-
observable parameters intervene (Figure 7).
•r :S×A×S→R is thereward function, weighing the transition(st,at,st+1)in the context of the achievement of
an arbitrary goal. For instance, a simple reward function for quickly moving along thex axis (Figure 11) could
be based on the absolute position of the robot along thex axis (pxt), present negative penalties for falling over
(measured frompzt) and a introduce bonuses˙pxt for speed,r(st,at,st+1)≡r(s t) =p xt·˙pxt− 1
pzt
.
Lastly,γ∈ [0, 1)represent the discount factor regulating preference for immediate versus long-term reward (with an
effective horizon equal to 1
1−γ), andρis the distribution overSfor the MDP’sinitial,s 0∼ρ.
Therefore, a length-Ttrajectoryis the (random) sequence
τ= (s 0,a 0,r 0,s 1,a 1,r 1,...,s T−1,aT−1,rT−1,sT ),(3)
with per-step rewards defined asrt =r(st,at,st+1)for ease of notation. Interestingly, assuming both the environment
dynamics and conditional distribution over actions given states—i.e., thepolicy—to beMarkovian:
P(st+1|st,at,st−1,at−1,...s 0,a 0) =P(s t+1|st,at)(4)
P(at|st,at−1,st−1,s 0,a 0) =P(a t|st),(5)
the probability of observing a given trajectoryτfactorizes into:
P(τ) =P(s 0)
T−1Y
t=0
P(st+1|st,at)P(a t|st).(6)
Policies P(at|st)are typically indicated asπ(at|st), often parametrized viaθ, yieldingπθ(at|st), and are traine by
optimizing the (discounted)returnassociated to a given τ, i.e. the (random) sum of measured rewards over an
arbitrary trajectory,
G(τ) =
T−1X
t=0
γtrt.
18

[PAGE 19]

Figure 13|Popular RL algorithms. See Achiam (2018) for a complete list of citations.
In that, agents seek to learn control strategies (policies,πθ) maximizing the expected returnEτ∼πθG(τ). For a given
dynamicsD—i.e., for a given problem—taking the expectation over the (possibly random) trajectories resulting from
acting according to a certain policy provides a direct, goal-conditioned ordering in the space of all the possible policies
Π, yielding the (maximization) targetJ: Π7→R
J(πθ) =E τ∼Pθ;D[G(τ)],(7)
Pθ;D(τ) =ρ
T−1Y
t=0
D(st,at,st+1)π θ(at|st).(8)
Crucially, in the RL framework the agent is assumed to onlyobservethe environment dynamics and not to intervene
on them, and thus eq. 7 varies exclusively with the policy followed. In turn, MDPs naturally provide a framework
to optimize over the space of the possible behaviors an agent might enact (π∈ Π), searching for theoptimal policy
π∗ = arg maxθJ(πθ), whereθ is the parametrization adopted by the policy setΠ :πθ∈ Π,∀θ . Besides providing a
target for policy search,G(τ)can also be used to discriminate between statesst and st,at pairs. Given any state
s∈S—e.g., given a configurationqof a robot—thestate-valuefunction
Vπ(s) =E τ∼π

G(τ)
s0 =s

can be used to discriminate between desirable and undesirable state in terms of long-term (discounted) reward
maximization, under a given policyπ. Similarily, thestate-actionvalue function also conditions the cumulative
discounted reward on selecting actionawhen ins, and thereafter act according toπ,
Qπ(s,a) =E τ∼π

G(τ)
s0 =s,a 0 =a

.
Importantly, value functions are interrelated:
Qπ(st,at) =E st+1∼P(•|st,at)[rt +γV π(st+1)](9)
Vπ(st) =E at∼π(•|st)[Qπ(st,at)],(10)
inducing an ordering over states and state-action pairs underπ, and value functions are thus central to most RL
algorithms. A variety of algorithms have been developed in RL attempting to find (approximate) solutions to the
problem of maximizing cumulative reward (we report some in Figure 13).
Popular approaches to continuous state and action space—such as those studied within robotics—include Schulman
et al. (2017a, TRPO), Schulman et al. (2017b, PPO) and Haarnoja et al. (2018, SAC). Across manipulation (Akkaya
19

[PAGE 20]

Figure 14 | Simulated (left) vs. real-world (right) OpenDuck. Discrepancies in the simulation dynamics (reality gap) pose risks
to policy transfer.
et al., 2019) and locomotion problems (Lee et al., 2020), RL proved extremely effective in providing a platform to (1)
leverage a unified, streamlined perception-to-action pipeline, (2) natively integrate propioperception with multi-modal
high-dimensional sensory streams (3) disregard a description of the environment dynamics, by focusing on observed
interaction data rather than modeling, and (4) anchor policies in the experience collected and stored in datasets. For
a more complete survey of applications of RL to robotics, we refer the reader to Kober et al.; Tang et al. (2025).
3.2 Real-world RL for Robotics
Streamlined end-to-end control pipelines, data-driven feature extraction and a disregard for explicit modeling in favor
of interaction data are all features of RL for robotics. However, RL still suffers from limitations concerning safety and
learning efficiency, particularly pressing for real-world robotics applications.
First, especially early in training, actions are typically explorative, and thus may be erractic. On physical systems,
untrained policies may command high velocities, self-collisiding configurations, or torques exceeding joint limits,
leading to wear and potential hardware damage. Mitigating these risks requires external safeguards (e.g., watchdogs,
safety monitors, emergency stops), often incuring in a high degree of human supervision. Further, in the typical
episodic setting considered in most robotics problems, experimentation is substantially slowed down by the need to
manually reset the environment over the course of training, a time-consuming and error-prone process. Second, learning
efficiently remains problematic in RL, limiting the applicability of RL in real-world robotics due to consequently
prohibitive timescales of training. Even strong algorithms such as SAC (Haarnoja et al., 2018) typically require a
large numbers of transitions{(st,at,rt,st+1)}N
t=1. On real-world hardware, generating this data is time-consuming.
Training RL policies in simulation (Tobin et al., 2017) addresses both issues, eliminating physical risk and dramatically
increasing throughput. Yet, simulators require significant modeling effort, and rely on assumptions (simplified physical
modeling, instantaneous actuation, static environmental conditions, etc.) limiting the possibilities to transfer the
policies learned in simulation, due the discrepancy between real and simulated environments (reality gap, Figure 14).
Domain randomization(Tobin et al., 2017) (DR) is a popular technique to overcome the reality gap, and consists in
randomizing the parameters of the simulated environment during training, aiming at inducing robustness to specific
disturbances. In this, DR is typically employed to increase the diversity of scenarios over the course of training,
improving on the performace sim-to-real transferred policies (Akkaya et al., 2019; Antonova et al., 2017; Ji et al.,
2023). In practice, DR is performed training in simulation on simulated dynamicsD, further parametrized asD≡D ξ,
with adynamics(random) vector ξ drawn an arbitrary distribution,ξ∼ Ξ. For instance, one could decide to
randomize the friction coefficient of the surface in a locomotion task (Figure 15), or the center of mass of an object
for a manipulation task. Over the course of training—typically at each episode’s reset—a newξ is drawn, and used to
specify the environment’s dynamics for that episode.
While effective in transfering policies across the reality gap in real-world robotics (Tobin et al., 2017; Akkaya et al.,
2019; Ji et al., 2023; Tiboni et al., 2024), DR often requires extensive manual engineering. First, identifying which
20

[PAGE 21]

Figure 15 | The same locomotion task can be carried out in different (simulated) domains (exemplified by the difference in
terrains) at training time, resulting to increased robustness over diverse environment dynamics.
parameters to randomize—i.e., thesupportsupp(Ξ)ofΞ—is an inherently task specific process. When locomoting over
different terrains, choosing to randomize the friction coefficient is a reasonable choice, yet not completely resolutive as
other factors (lightning conditions, external temperature, joints’ fatigue, etc.) may prove just as important in practice,
making selecting these parameters yet another source of brittlness.
Selecting the dynamics distributionΞis also non-trivial. On the one hand, distributions with low entropy might risk
to cause failure at transfer time, due to the limited robustness induced over the course of training. On the other hand,
excessive randomization may cause over-regularization and hinder performance (Margolis et al., 2022). Consequently,
the research community investigated approaches to automatically select the randomization distributionΞ, using
signals from the training process or tuning it to reproduce observed real-world trajectories. Akkaya et al. (2019)
use a parametric uniform distributionU(a,b )asΞ, widening the bounds a,b as training progresses and the agent’s
performance improves (AutoDR). While effective, AutoDR requires significant tuning—the bounds are widened by a
fixed, pre-specified amount∆along—and may disregard data when performancedoes notimprove after a distribution
update (Tiboni et al., 2024). Tiboni et al. (2024) propose a similar method to AutoDR (DORAEMON) to evolveΞ
based on the training signal, but with the key difference of explicitly maximizing the entropy of a parametric Beta
distribution—inherently more flexible than uniform distributions—with learned updates instead of fixed∆. In this,
DORAEMON proves particularly effective at dynamically increasing the entropy levels of the training distribution by
employing an outer-loop max-entropy objective, tackled under performance constraints in the inner-loop RL problem.
Other approaches to automatically perform DR consist in specifically tuningΞto align as much as possible the
simulation and real-world domains. For instance, Chebotar et al. (2019) interleave in-simulation policy training with
repeated real-world policy rollouts used to adjustΞbased on real-world data, while Tiboni et al. (2023) leverage a
single, pre-collected set of real-world trajectories and tuneΞunder a simple likelihood objective.
While DR has shown promise, it does not address the main limitation that, even under the assumption that an ideal
distributionΞwas available, many robotics problems cannot be simulated with high-enough fidelity under practical
computational constraints. Simulating contact-rich manipulation of possibly deformable or soft materials—i.e.,folding
a piece of clothing—can prove time-intensive, limiting the benefits of in-simulation training.
A perhaps more foundamental limitation of RL for robotics is the general unavailability of complicated tasks’dense
reward function, the design of which is essentially based on human expertise, ingenuity and trial-and-error. In
practice,sparsereward functions can be used to conclude whether one specific goal has been attained—has this t-shirt
been correctly folded?—but unfortunately incur in more challenging learning. As a result, despite notable successes,
deploying RL directly on real-world robots at scale remains challenging.
To make the most of (1) the growing number of openly available datasets and (2) relatively inexpensive robots like the
SO-100, RL could (1) be anchored in already-collected trajectories—limiting erratic and dangerous exploration—and
(2) train in the real-world directly—bypassing the aforementioned issues with low-fidelity simulations. In such a
context, sample-efficient learning is also paramount, as training on the real-world is inherently time-bottlenecked.
Off-policy algorithms like Soft Actor-Critic (SAC) (Haarnoja et al., 2018) tend to be more sample efficient then their
on-policy counterpart (Schulman et al., 2017b), due to the presence areplay bufferused over the course of training.
Other than allowing to re-use past transitions(st,at,rt,st+1), the replay buffer can also accomodate for the injection
of previously-collected data in the training process (Ball et al., 2023). Using expert demonstrations to guide learning
together with learned rewards, RL can be effectively carried out in the real-world (Luo et al., 2025). Interestingly,
when complemented with in-training human interventions, real-world RL agents have been shown to learn policies
with near-perfect success rates on challenging manipulation tasks in 1-2 hours (Luo et al., 2024).
21

[PAGE 22]

Sample-efficient RLIn an MDP, the optimal policy π∗ can be derived from its associatedQ-function, Q∗≡Q π∗,
and in particular the optimal action(s)µ(st)can be selected maximizing the optimalQ-function over the action space,
µ(st) = max
at∈A
Q∗(st,at).
Interestingly, theQ∗-function satisfies a recursive relationship (Bellman equation) based on a very natural intuition2:
[...] If the optimal valueQ∗(st+1,at+1)of the [state]st+1 was known for all possible actionsat+1, then
the optimal strategy is to select the actionat+1 maximizing the expected value ofrt +γQ∗(st+1,at+1)
Q∗(st,at) =E st+1∼P(•|st,at)

rt +γmax
at+1∈A
Q∗(st+1,at+1)
st,at

In turn, the optimalQ-function is guaranteed to be self-consistent by definition.Value-iterationmethods exploit this
relationship (and/or its state-value counterpart,V∗(st)) by iteratively updating an initial estimate ofQ∗, Qk using
the Bellman equation as update rule (Q-learning):
Qi+1(st,at)←E st+1∼P(•|st,at)

rt +γmax
at+1∈A
Qi(st+1,at+1)
st,at

, i= 0,1,2,...,K
Then, one can derive the (ideally, near-optimal) policy by explicitly maximizing over the action space the final (ideally,
near-optimal) estimateQK≈Q∗ at each timestep. Indeed, one can show that under certain assumptions on the MDP
considered,Q K→Q∗asK→∞.
Effective in its early applications to small-scale discrete problems, vanilla Q-learning was found complicated to scale
to largeS×Aproblems, in which storingQ:S×A7→Ralone might result prohibitive. Also, vanilla Q-learning is
not directly usable forcontinuous, unstructured state-action space MPDs, such as those considered in robotics. In
their seminal work onDeep Q-Learning(DQN), Mnih et al. (2013) propose learning Q-values using deep convolutional
neural networks, thereby accomodating for large and even unstructuredstatespaces. DQN parametrizes the Q-function
using a neural network with parametersθ, updating the parameters by sequentially minimizing the expected squared
temporal-difference error (TD-error,δi):
L(θi) =E (st,at)∼χ(•)

(yi−Qθi(st,at)| {z }
δi
)2
,(11)
yi =E st+1∼P(•|st,at)

rt +γmax
at∈A
Qθi−1(st+1,at+1)

,(12)
where χ represents a behavior distribution over state-action pairs. Crucially,χ can in principle be different from the
policy being followed, effectively allowing to reuse prior data stored in areplay bufferD in the form of(st,at,rt,st+1)
transitions, used to form the TD-targetyi, TD-errorδi and loss function eq. 11 via Monte-Carlo (MC) estimates.
While effective in handling large, unstructured state spaces for discrete action-space problems, DQN’s application to
continous control problems proved challenging. Indeed, in the case of high-capacity function approximators such as
neural networks, solvingmaxat∈AQθ(st,at)at each timestep is simply unfeasible due to the (1) continous nature
of the action space (A⊂R n for somen) and (2) impossibility to express the policy with a cheap (ideally, even
closed-form) formulation, so thatmaxQθ could be solved analytically. Silver et al. (2014) tackle these fundamental
challenges by using adeterministicfunction of the statest as policy,µϕ(st) =at, parametrized byϕ. Thus, policies
can be iteratively refined updatingϕalong the direction:
dϕ =E st∼P(•)

∇ϕQ(st,at)|at=µϕ(st)

=E st∼P(•)

∇atQ(st,at)|at=µϕ(st)·∇ϕµ(st)

(13)
Provably, eq. 13 is thedeterministic policy gradient(DPG) of the policyµϕ (Silver et al., 2014), so that updates
ϕk+1←ϕ k +αdϕ are guaranteed to increase the (deterministic) cumulative discounted reward,J(µϕ). Lillicrap
et al. (2019) extended DPG to the case of (1) high-dimensional unstructured observations and (2) continuous action
spaces, introducing Deep Deterministic Policy Gradient (DDPG), an important algorithm in RL and its applications
to robotics. DDPG adopts a modified TD-target compared to eq. 12, by maintaining a policy network used to select
actions, yielding
yi =E st+1∼P(•|st,at)

rt +γQ θi−1(st+1,µϕ(st+1))

.(14)
2Quote from Mnih et al. (2013). The notation used has slightly been adapted for consistency with the rest of this tutorial.
22

[PAGE 23]

Similarily to DQN, DDPG also employs the same replay buffer mechanism, reusing past transitions over training for
increased sample efficiency and estimate the loss function via MC-estimates.
Soft Actor-Critic (SAC) (Haarnoja et al., 2018) is a derivation of DDPG in the max-entropy (MaxEnt) RL framework,
in which RL agents are tasked with maximizing the discounted cumulative reward, while acting as randomly as
possible. MaxEnt RL (Haarnoja et al., 2017) has proven particularly robust thanks to the development of diverse
behaviors, incentivized by its entropy-regularization formulation. In that, MaxEnt revisits the RL objectiveJ(π)to
specifically account for the policy entropyH(π(•|st)),
J(π) =
TX
t=0
E(st,at)∼χ[rt +αH(π(•|s t))].(15)
This modified objective results in thesoftTD-target:
yi =E st+1∼P(•|st,at)

rt +γ
 
Qθi−1(st+1,at+1)−αlogπ ϕ(at+1|st+1)

, a t+1∼π ϕ(•|st)(16)
Similarily to DDPG, SAC also maintains an explicit policy, trained under the same MaxEnt framework for the
maximization of eq. 15, updated using:
πk+1←arg min
π′∈Π
DKL

π′(•|st)

exp(Qπk(st,•))
Zπk(st)

(17)
The update rule provided in eq. 17 optimizes the policy while projecting it on a setΠof tractable distributions (e.g.,
Gaussians, Haarnoja et al. (2017)).
Sample-efficient, data-driven RLSampling( st,at,rt,st+1)from the replay bufferD conveniently allows to approx-
imate expectations for TD-target and TD-error through Monte-Carlo (MC) estimates. The replay bufferD also
proves extremely useful in maintaining a history of previous transitions and using it for training, improving on sample
efficiency. Furthermore, it also naturally provides an entry point to inject offline trajectories recorded by a human
demonstrator into the training process.
Reinforcement Learning with Prior Data (RLPD) (Ball et al., 2023) is an Offline-to-Online RL algorithm leveraging
prior data to effectively accelerate the training of a SAC agent. Unlike previous works on Offline-to-Online RL, RLPD
avoids any pre-training and instead only uses the available offline dataDoffline to improve online-learning from scratch.
During each training step, transitions from both the offline and online replay buffers are sampled in equal proportions,
and used in the underlying SAC routine. Together with other implementation details (using LayerNorm layers to
prevent value overestimation, and the use of ensembles techniques to form the TD-target), RLPD proves a particularly
simple yet effective approach to useDoffline for Offline-to-Online RL.
Sample-efficient, data-driven, real-world RLDespite the possibility to leverage offline data for learning, the
effectiveness of real-world RL training is still limited by the need to define a task-specific, hard-to-define reward
function. Further, even assuming to have access to a well-defined reward function, typical robotics pipelines rely
on augmenting propioperceptive inputs with camera streams, and thus even well-defined rewards would need to be
defined starting from unstructured observation—a challenging assumption in practice. In their technical report, Luo
et al. (2025) empirically address the needs (1) to define a reward function and (2) to use it starting from unstructured,
image observations. In particular, Luo et al. (2025, SERL) introduces a suite of tools streamlining training ofreward
classifiersc, as well as jointly learn forward-backward controllers to speed up real-world RL.
Reward classifiers are particularly useful in treating complex, dynamic tasks—e.g., folding a t-shirt—for which a
precise reward formulation is arbitrarily complex to obtain, or that do require significant shaping and are more easily
learned directly from demonstrations of success (e+) or failure (e−) states, rather than from a precise formulation
of rt, with a natural target for the reward classifier beingr(s) = logc (e+ verts). Furthermore, Luo et al. (2025)
demonstrate the benefits of learning separate (1)forwardand (2)backwardcontrollers—parametrized by separate
policies—where (1) the former learns to execute a task to completion and (2) the latter learns to reset the environment
to its initial state from terminal states, thereby aiding training in real-world episodic settings.
Lastly, in order to improve on the robustness of their approach to different goals while maintaing practical scalabil-
ity, Luo et al. (2025) introduced a modified state and action space, expressing proprioperceptive configurationsq and
actions ˙qin the frame of the end-effector pose att = 0. Randomizing the initial pose of the end-effector (s0), Luo
et al. (2025) achieved a similar result to that of manually randomizing the environment at every timestep, but with
23

[PAGE 24]

Figure 16 | (A) HIL-SERL allows for real-world training of high performance RL agents by building on top advancements
presented by of SAC, RLPD and SERL. (B) Example of human intervention during a HIL-SERL training process on a real-world
SO-100.
the benefit of maintaining the environment in the same condition across multiple training episodes, achieving higher
scalability of their method thanks to the increased practicality of their approach.
Building on off-policy deep Q-learning with replay buffers, entropy regularization for better exploration, expert
demonstrations to guide learning, and a series of tools and recommendations for real-world training using reward
classifiers (Figure 16), Luo et al. (2024) introduce human interactions during training, learning near-optimal policies
in challenging real-world manipulation tasks in 1-2 hours.
Human-in-the-Loop, Sample Efficient Robot reinforcement Learning (HIL-SERL) (Luo et al., 2024) augments offline-
to-online RL with targeted human corrections during training, and employs prior data to (1) train a reward classifier
and (2) bootstrap RL training on expert trajectories. While offline demonstrations provide the initial dataset seeding
learning and constraining early exploration, interactive, online corrections allow a human supervisor to intervene on
failure modes and supply targeted interventions, greatly aiding the learning process (Luo et al., 2024). Crucially,
human intervention data is stored inboththe offline and online replay buffers, differently from the autonomous
transitions generated at training time and stored in the online buffer only. In turn, given an intervention timestep
k∈ (0,T ), length-K human intervention data{shuman
k ,ahuman
k ,rhuman
k ,shuman
k+1 ,}K
k=1 is more likely to be sampled
than the data generated online during training, providing stronger supervision to the agent while still allowing for
autonomous learning. Empirically, HIL-SERL attains near-perfect success rates (99%+) on diverse manipulation
tasks within 1-2 hours of training (Luo et al., 2024), underscoring how offline datasets with online RL can markedly
improve stability and data efficiency, and ultimately even allow real-world RL-training.
3.2.1 Code Example: Real-world RL
This example shows how to use the HIL-SERL implementation supported bylerobot. This code example is organized
into four parts: we first show how to train a reward classifier from a custom set of demonstrations, then define
the Actor and Learner components, and finally, we bring them together in a complete script showing how to use
HIL-SERL in practice.
At a higher level, the HIL-SERL architecture (Figure 17) relies on two main components:
• An Actor, running a frozen policy network used to interact with the environment and obtain observations.
Observations are used to both condition the frozen actor in selecting the action to enact, and to form(st,at,rt,st+1)
transitions that are shared with theLearner. Rewards are inferred using a custom, learned reward classifier trained
on a dataset of offline demonstrations.
• A Learner, used to optimize the policy’s parametersθ for maximum expected return. The learner samples batches
24

[PAGE 25]

Figure 17|HIL-SERL is a SOTA RL algorithm for training control policies directly in the real-world. Its implementation in
lerobot relies on a decoupled actor-learner architecture, communicating over processes (and possibly networks) with queues
used to share (1) transitions(st,a t,r t,s t+1)and (2) parametersθ.
of offline data from online and offline buffers in equal proportion (Ball et al., 2023), and shares updated parameters
with theActor.
The HIL-SERL architecture presented in this example can be exclusively run locally, but the implementation in
lerobotalso allows theActorandLearnerto run on two separate machines connected by the network.
Code 3: Training a Reward Classifier
https://github.com/fracapuano/robot-learning-tutorial/blob/main/snippets/ch3/01_reward_classifier.py
1import torch
2
3from lerobot . da ta set s . l e r o b o t _ d a t a s e t import L e R o b o t D a t a s e t
4from lerobot . po li cie s . factory import make_policy , m a k e _ p r e _ p o s t _ p r o c e s s o r s
5from lerobot . po li cie s . sac . r e w a r d _ m o d e l . c o n f i g u r a t i o n _ c l a s s i f i e r import R e w a r d C l a s s i f i e r C o n f i g
6
7# Device to use for tr ai ni ng
8device = " mps " # or " cuda " , or " cpu "
9
10# Load the dataset used for tr ai ni ng
11repo_id = " lerobot / e x a m p l e _ h i l _ s e r l _ d a t a s e t "
12dataset = L e R o b o t D a t a s e t ( repo_id )
13
14# C o n f i g u r e the policy to extract f ea tu re s from the image frames
15c a m e r a _ k e y s = dataset . meta . c a m e r a _ k e y s
16
17config = R e w a r d C l a s s i f i e r C o n f i g (
18n u m _ c a m e r a s = len ( c a m e r a _ k e y s ) ,
19device = device ,
20# b ac kb on e model to extract f ea tur es from the image frames
21m o d e l _ n a m e = " m i c r o s o f t / resnet -18 " ,
22)
23
24# Make policy , preprocessor , and o p t i m i z e r
25policy = m a k e _ p o l i c y ( config , ds_meta = dataset . meta )
26o p t i m i z e r = config . g e t _ o p t i m i z e r _ p r e s e t (). build ( policy . p a r a m e t e r s ())
27preprocessor , _ = m a k e _ p r e _ p o s t _ p r o c e s s o r s ( p o l i c y _ c f g = config , d a t a s e t _ s t a t s = dataset . meta . stats )
25

[PAGE 26]

28
29
30# your HF u se rna me and model repo id for the reward c l a s s i f i e r
31c l a s s i f i e r _ i d = " lerobot / r e w a r d _ c l a s s i f i e r _ h i l _ s e r l _ e x a m p l e "
32
33# I n s t a n t i a t e a d a t a l o a d e r
34d a t a l o a d e r = torch . utils . data . D a t a L o a d e r ( dataset , b a t c h _ s i z e =16 , shuffle = True )
35
36# Tr ai ni ng loop
37n u m _ e p o c h s = 5
38for epoch in range ( n u m _ e p o c h s ):
39t o t a l _ l o s s = 0
40t o t a l _ a c c u r a c y = 0
41for batch in d a t a l o a d e r :
42# P r e p r o c e s s the batch and move it to the correct device .
43batch = p r e p r o c e s s o r ( batch )
44
45# Forward pass
46loss , o u t p u t _ d i c t = policy . forward ( batch )
47
48# Ba ck war d pass and o p t i m i z a t i o n
49o p t i m i z e r . z e r o _ g r a d ()
50loss . b ac kw ar d ()
51o p t i m i z e r . step ()
52
53t o t a l _ l o s s += loss . item ()
54t o t a l _ a c c u r a c y += o u t p u t _ d i c t [ " a ccu ra cy " ]
55
56av g_ los s = t o t a l _ l o s s / len ( d a t a l o a d e r )
57a v g _ a c c u r a c y = t o t a l _ a c c u r a c y / len ( d a t a l o a d e r )
58print (
59f " Epoch { epoch + 1}/{ n u m _ e p o c h s } , Loss : { av g_ lo ss :.4 f } , Ac cu rac y : { a v g _ a c c u r a c y :.2 f }% "
60)
61
62print ( " T rai ni ng f in is he d ! " )
63
64# You can now save the trained policy .
65policy . p u s h _ t o _ h u b ( c l a s s i f i e r _ i d )
Code 4: Defining theActor
https://github.com/fracapuano/robot-learning-tutorial/blob/main/snippets/ch3/02_actor.py
1import m u l t i p r o c e s s i n g as mp
2from queue import Empty
3
4import torch
5from pathlib import Path
6
7from lerobot . envs . configs import H I L S e r l R o b o t E n v C o n f i g
8from lerobot . po li cie s . sac . m o d e l i n g _ s a c import S A C P o l i c y
9from lerobot . po li cie s . sac . r e w a r d _ m o d e l . m o d e l i n g _ c l a s s i f i e r import C l a s s i f i e r
10from lerobot . rl . g y m _ m a n i p u l a t o r import m a k e _ r o b o t _ e n v
11from lerobot . t e l e o p e r a t o r s . utils import T e l e o p E v e n t s
12
13M A X _ E P I S O D E S = 5
14M A X _ S T E P S _ P E R _ E P I S O D E = 20
15
16def m a k e _ p o l i c y _ o b s ( obs , device : torch . device = " cpu " ):
17return {
18" o b s e r v a t i o n . state " : torch . f r o m _ n u m p y ( obs [ " a g e n t _ p o s " ]). float (). u n s q u e e z e (0). to ( device ) ,
19**{
20f " o b s e r v a t i o n . image .{ k } " :
21torch . f r o m _ n u m p y ( obs [ " pixels " ][ k ]). float (). u n s q u e e z e (0). to ( device )
22for k in obs [ " pixels " ]
23} ,
24}
26

[PAGE 27]

25
26def r u n _ a c t o r (
27t r a n s i t i o n s _ q u e u e : mp . Queue ,
28p a r a m e t e r s _ q u e u e : mp . Queue ,
29s h u t d o w n _ e v e n t : mp . Event ,
30p o l i c y _ a c t o r : SACPolicy ,
31r e w a r d _ c l a s s i f i e r : Classifier ,
32env_cfg : H I L S e r l R o b o t E n v C o n f i g ,
33device : torch . device = " mps " ,
34o u t p u t _ d i r e c t o r y : Path | None = None
35):
36" " " The actor process - i n t e r a c t s with e n v i r o n m e n t and co ll ec ts data .
37The policy is frozen and only the p a r a m e t e r s are updated , popping the most recent ones
38from a queue . " " "
39p o l i c y _ a c t o r . eval ()
40p o l i c y _ a c t o r . to ( device )
41
42r e w a r d _ c l a s s i f i e r . eval ()
43r e w a r d _ c l a s s i f i e r . to ( device )
44
45# Create robot e n v i r o n m e n t inside the actor process
46env , t e l e o p _ d e v i c e = m a k e _ r o b o t _ e n v ( env_cfg )
47
48try :
49for episode in range ( M A X _ E P I S O D E S ):
50if s h u t d o w n _ e v e n t . is_set ():
51break
52
53obs , _info = env . reset ()
54e p i s o d e _ r e w a r d = 0.0
55step = 0
56e p i s o d e _ t r a n s i t i o n s = []
57
58print ( f " [ ACTOR ] St art in g episode { episode + 1} " )
59
60while step < M A X _ S T E P S _ P E R _ E P I S O D E and not s h u t d o w n _ e v e n t . is_set ():
61try :
62n e w _ p a r a m s = p a r a m e t e r s _ q u e u e . g e t _ n o w a i t ()
63p o l i c y _ a c t o r . l o a d _ s t a t e _ d i c t ( n e w _ p a r a m s )
64print ( " [ ACTOR ] Updated policy p a r a m e t e r s from learner " )
65except Empty : # No new updated p a r a m e t e r s a v a i l a b l e from learner , waiting
66pass
67
68# Get action from policy
69p o l i c y _ o b s = m a k e _ p o l i c y _ o b s ( obs , device = device )
70# pre di ct s a single action , not a chunk of actions !
71a c t i o n _ t e n s o r = p o l i c y _ a c t o r . s e l e c t _ a c t i o n ( p o l i c y _ o b s )
72action = a c t i o n _ t e n s o r . squeeze (0). cpu (). numpy ()
73
74# Step e n v i r o n m e n t
75next_obs , _env_reward , terminated , truncated , _info = env . step ( action )
76done = t e r m i n a t e d or t r u n c a t e d
77
78# Predict reward
79p o l i c y _ n e x t _ o b s = m a k e _ p o l i c y _ o b s ( next_obs , device = device )
80reward = r e w a r d _ c l a s s i f i e r . p r e d i c t _ r e w a r d ( p o l i c y _ n e x t _ o b s )
81
82if reward >= 1.0: # success de te ct ed ! halt episode
83if not done :
84t e r m i n a t e d = True
85done = True
86
87# In HIL - SERL , human i n t e r v e n t i o n s come from the teleop device
88i s _ i n t e r v e n t i o n = False
89if hasattr ( teleop_device , " g e t _ t e l e o p _ e v e n t s " ):
90# Real i n t e r v e n t i o n d e t e c t i o n from teleop device
91t e l e o p _ e v e n t s = t e l e o p _ d e v i c e . g e t _ t e l e o p _ e v e n t s ()
92i s _ i n t e r v e n t i o n = t e l e o p _ e v e n t s . get ( T e l e o p E v e n t s . IS_INTERVENTION , False )
93
94# Store t r a n s i t i o n with i n t e r v e n t i o n me tad at a
27

[PAGE 28]

95t r a n s i t i o n = {
96" state " : policy_obs ,
97" action " : action ,
98" reward " : float ( reward ) if hasattr ( reward , " item " ) else reward ,
99" n e x t _ s t a t e " : policy_next_obs ,
100" done " : done ,
101" t r u n c a t e d " : truncated ,
102" c o m p l e m e n t a r y _ i n f o " : {
103" i s _ i n t e r v e n t i o n " : is_intervention ,
104} ,
105}
106
107e p i s o d e _ t r a n s i t i o n s . append ( t r a n s i t i o n )
108
109e p i s o d e _ r e w a r d += reward
110step += 1
111
112obs = ne xt_ ob s
113
114if done :
115break
116
117# Send episode t r a n s i t i o n s to learner
118t r a n s i t i o n s _ q u e u e . p u t _ n o w a i t ( e p i s o d e _ t r a n s i t i o n s )
119
120except K e y b o a r d I n t e r r u p t :
121print ( " [ ACTOR ] I n t e r r u p t e d by user " )
122finally :
123# Clean up
124if hasattr ( env , " robot " ) and env . robot . i s _ c o n n e c t e d :
125env . robot . d i s c o n n e c t ()
126if t e l e o p _ d e v i c e and hasattr ( teleop_device , " d i s c o n n e c t " ):
127t e l e o p _ d e v i c e . d i s c o n n e c t ()
128if o u t p u t _ d i r e c t o r y is not None :
129p o l i c y _ a c t o r . s a v e _ p r e t r a i n e d ( o u t p u t _ d i r e c t o r y )
130print ( f " [ ACTOR ] Latest actor policy saved at : { o u t p u t _ d i r e c t o r y } " )
131
132print ( " [ ACTOR ] Actor process fi nis he d " )
Code 5: Defining theLearner
https://github.com/fracapuano/robot-learning-tutorial/blob/main/snippets/ch3/03_learner.py
1import m u l t i p r o c e s s i n g as mp
2from queue import Empty , Full
3
4import torch
5import torch . optim as optim
6
7from lerobot . po li cie s . sac . m o d e l i n g _ s a c import S A C P o l i c y
8from lerobot . rl . buffer import R e p l a y B u f f e r
9
10L O G _ E V E R Y = 10
11S E N D _ E V E R Y = 10
12
13def r u n _ l e a r n e r (
14t r a n s i t i o n s _ q u e u e : mp . Queue ,
15p a r a m e t e r s _ q u e u e : mp . Queue ,
16s h u t d o w n _ e v e n t : mp . Event ,
17p o l i c y _ l e a r n e r : SACPolicy ,
18o n l i n e _ b u f f e r : ReplayBuffer ,
19o f f l i n e _ b u f f e r : ReplayBuffer ,
20lr : float = 3e -4 ,
21b a t c h _ s i z e : int = 32 ,
22device : torch . device = " mps " ,
23):
24" " " The learner process - trains SAC policy on t r a n s i t i o n s s tre am ed from the actor ,
28

[PAGE 29]

25up da tin g p a r a m e t e r s for the actor to adopt . " " "
26p o l i c y _ l e a r n e r . train ()
27p o l i c y _ l e a r n e r . to ( device )
28
29# Create Adam o p t i m i z e r from scratch - simple and clean
30o p t i m i z e r = optim . Adam ( p o l i c y _ l e a r n e r . p a r a m e t e r s () , lr = lr )
31
32print ( f " [ LEARNER ] Online buffer ca pa ci ty : { o n l i n e _ b u f f e r . c ap ac ity } " )
33print ( f " [ LEARNER ] Offline buffer c ap ac ity : { o f f l i n e _ b u f f e r . ca pa ci ty } " )
34
35t r a i n i n g _ s t e p = 0
36
37while not s h u t d o w n _ e v e n t . is_set ():
38# re tr iev e i nco mi ng t r a n s i t i o n s from the actor process
39try :
40t r a n s i t i o n s = t r a n s i t i o n s _ q u e u e . get ( timeout =0.1)
41for t r a n s i t i o n in t r a n s i t i o n s :
42# HIL - SERL : Add ALL t r a n s i t i o n s to online buffer
43o n l i n e _ b u f f e r . add (** t r a n s i t i o n )
44
45# HIL - SERL : Add ONLY human i n t e r v e n t i o n t r a n s i t i o n s to offline buffer
46i s _ i n t e r v e n t i o n = \
47t r a n s i t i o n . get ( " c o m p l e m e n t a r y _ i n f o " , {}). get ( " i s _ i n t e r v e n t i o n " , False )
48if i s _ i n t e r v e n t i o n :
49o f f l i n e _ b u f f e r . add (** t r a n s i t i o n )
50print (
51f " [ LEARNER ] Human i n t e r v e n t i o n de te cte d ! "
52f " Added to offline buffer ( now { len ( o f f l i n e _ b u f f e r )} t r a n s i t i o n s ) "
53)
54
55except Empty :
56pass # No t r a n s i t i o n s available , co nti nu e
57
58# Train if we have enough data
59if len ( o n l i n e _ b u f f e r ) >= p o l i c y _ l e a r n e r . config . o n l i n e _ s t e p _ b e f o r e _ l e a r n i n g :
60# Sample from online buffer ( a u t o n o m o u s + human data )
61o n l i n e _ b a t c h = o n l i n e _ b u f f e r . sample ( b a t c h _ s i z e // 2)
62
63# Sample from offline buffer ( human d e m o n s t r a t i o n s only )
64o f f l i n e _ b a t c h = o f f l i n e _ b u f f e r . sample ( b a t c h _ s i z e // 2)
65
66# Combine batches - this is the key HIL - SERL m e c h a n i s m !
67batch = {}
68for key in o n l i n e _ b a t c h . keys ():
69if key in o f f l i n e _ b a t c h :
70batch [ key ] = torch . cat ([ o n l i n e _ b a t c h [ key ] , o f f l i n e _ b a t c h [ key ]] , dim =0)
71else :
72batch [ key ] = o n l i n e _ b a t c h [ key ]
73
74loss , _ = p o l i c y _ l e a r n e r . forward ( batch )
75
76o p t i m i z e r . z e r o _ g r a d ()
77loss . ba ck wa rd ()
78o p t i m i z e r . step ()
79t r a i n i n g _ s t e p += 1
80
81if t r a i n i n g _ s t e p % L O G _ E V E R Y == 0:
82print (
83f " [ LEARNER ] T ra in in g step { t r a i n i n g _ s t e p } , Loss : { loss . item ():.4 f } , "
84f " Buffers : Online ={ len ( o n l i n e _ b u f f e r )} , Offline ={ len ( o f f l i n e _ b u f f e r )} "
85)
86
87# Send updated p a r a m e t e r s to actor every 10 t ra in ing steps
88if t r a i n i n g _ s t e p % S E N D _ E V E R Y == 0:
89try :
90s t a t e _ d i c t = { k : v . cpu () for k , v in p o l i c y _ l e a r n e r . s t a t e _ d i c t (). items ()}
91p a r a m e t e r s _ q u e u e . p u t _ n o w a i t ( s t a t e _ d i c t )
92print ( " [ LEARNER ] Sent updated p a r a m e t e r s to actor " )
93except Full :
94# Missing write due to queue not being co ns um ed ( should happen rarely )
29

[PAGE 30]

95pass
96
97print ( " [ LEARNER ] Learner process f in is hed " )
Code 6: Using HIL-SERL
https://github.com/fracapuano/robot-learning-tutorial/blob/main/snippets/ch3/04_hil_serl.py
1import m u l t i p r o c e s s i n g as mp
2import signal
3from typing import C al la bl e
4from pathlib import Path
5
6from lerobot . da ta set s . l e r o b o t _ d a t a s e t import L e R o b o t D a t a s e t
7from lerobot . da ta set s . utils import h w _ t o _ d a t a s e t _ f e a t u r e s
8from lerobot . envs . configs import H I L S e r l P r o c e s s o r C o n f i g , H I L S e r l R o b o t E n v C o n f i g
9from lerobot . po li cie s . sac . c o n f i g u r a t i o n _ s a c import S A C C o n f i g
10from lerobot . po li cie s . sac . m o d e l i n g _ s a c import S A C P o l i c y
11from lerobot . po li cie s . sac . r e w a r d _ m o d e l . m o d e l i n g _ c l a s s i f i e r import C l a s s i f i e r
12from lerobot . rl . buffer import R e p l a y B u f f e r
13from lerobot . rl . g y m _ m a n i p u l a t o r import m a k e _ r o b o t _ e n v
14from lerobot . robots . s o 1 0 0 _ f o l l o w e r import S O 1 0 0 F o l l o w e r C o n f i g
15from lerobot . t e l e o p e r a t o r s . s o 1 0 0 _ l e a d e r import S O 1 0 0 L e a d e r C o n f i g
16
17
18r u n _ l e a r n e r : Ca ll abl e = ... # use / modify the f u n c t i o n s defined earlier
19r u n _ a c t o r : C al lab le = ...
20
21" " " Main f un ct io n - c o o r d i n a t e s actor and learner p r o c e s s e s . " " "
22
23device = " mps " # or " cuda " or " cpu "
24o u t p u t _ d i r e c t o r y = Path ( " outputs / r o b o t _ l e a r n i n g _ t u t o r i a l / hi l_ ser l " )
25o u t p u t _ d i r e c t o r y . mkdir ( parents = True , ex is t_o k = True )
26
27# find ports using lerobot - find - port
28f o l l o w e r _ p o r t = ...
29l e a d e r _ p o r t = ...
30
31# the robot ids are used the load the right c a l i b r a t i o n files
32f o l l o w e r _ i d = ...
33l e a d e r _ i d = ...
34
35# A p r e t r a i n e d model ( to be used in - d i s t r i b u t i o n !)
36r e w a r d _ c l a s s i f i e r _ i d = " lerobot / r e w a r d _ c l a s s i f i e r _ h i l _ s e r l _ e x a m p l e "
37r e w a r d _ c l a s s i f i e r = C l a s s i f i e r . f r o m _ p r e t r a i n e d ( r e w a r d _ c l a s s i f i e r _ i d )
38
39r e w a r d _ c l a s s i f i e r . to ( device )
40r e w a r d _ c l a s s i f i e r . eval ()
41
42M A X _ E P I S O D E S = 5
43M A X _ S T E P S _ P E R _ E P I S O D E = 20
44
45# Robot and e n v i r o n m e n t c o n f i g u r a t i o n
46r o b o t _ c f g = S O 1 0 0 F o l l o w e r C o n f i g ( port = follower_port , id = f o l l o w e r _ i d )
47t e l e o p _ c f g = S O 1 0 0 L e a d e r C o n f i g ( port = leader_port , id = l e a d e r _ i d )
48p r o c e s s o r _ c f g = H I L S e r l P r o c e s s o r C o n f i g ( c o n t r o l _ m o d e = " leader " )
49
50env_cfg = H I L S e r l R o b o t E n v C o n f i g ( robot = robot_cfg , teleop = teleop_cfg , p r o c e s s o r = p r o c e s s o r _ c f g )
51
52# Create robot e n v i r o n m e n t
53env , t e l e o p _ d e v i c e = m a k e _ r o b o t _ e n v ( env_cfg )
54
55o b s _ f e a t u r e s = h w _ t o _ d a t a s e t _ f e a t u r e s ( env . robot . o b s e r v a t i o n _ f e a t u r e s , " o b s e r v a t i o n " )
56a c t i o n _ f e a t u r e s = h w _ t o _ d a t a s e t _ f e a t u r e s ( env . robot . action_features , " action " )
57
58# Create SAC policy for action s e l e c t i o n
59p o l i c y _ c f g = S A C C o n f i g (
30

[PAGE 31]

60device = device ,
61i n p u t _ f e a t u r e s = obs_features ,
62o u t p u t _ f e a t u r e s = action_features ,
63)
64
65p o l i c y _ a c t o r = S A C P o l i c y ( p o l i c y _ c f g )
66p o l i c y _ l e a r n e r = S A C P o l i c y ( p o l i c y _ c f g )
67
68d e m o n s t r a t i o n s _ r e p o _ i d = " lerobot / e x a m p l e _ h i l _ s e r l _ d a t a s e t "
69o f f l i n e _ d a t a s e t = L e R o b o t D a t a s e t ( repo_id = d e m o n s t r a t i o n s _ r e p o _ i d )
70
71# Online buffer : i n i t i a l i z e d from scratch
72o n l i n e _ r e p l a y _ b u f f e r = R e p l a y B u f f e r ( device = device , s t a t e _ k e y s = list ( o b s _ f e a t u r e s . keys ()))
73# Offline buffer : Created from dataset ( pre - p o p u l a t e d it with d e m o n s t r a t i o n s )
74o f f l i n e _ r e p l a y _ b u f f e r = R e p l a y B u f f e r . f r o m _ l e r o b o t _ d a t a s e t (
75l e r o b o t _ d a t a s e t = offline_dataset , device = device , s t a t e _ k e y s = list ( o b s _ f e a t u r e s . keys ())
76)
77
78# Create c o m m u n i c a t i o n c ha nn el s between learner and actor p r o c e s s e s
79t r a n s i t i o n s _ q u e u e = mp . Queue ( maxsize =10)
80p a r a m e t e r s _ q u e u e = mp . Queue ( maxsize =2)
81s h u t d o w n _ e v e n t = mp . Event ()
82
83
84# Signal handler for gr ac ef ul s hu td own
85def s i g n a l _ h a n d l e r ( sig ):
86print ( f " \ nSignal { sig } received , s hu tt ing down ... " )
87s h u t d o w n _ e v e n t . set ()
88
89
90signal . signal ( signal . SIGINT , s i g n a l _ h a n d l e r )
91signal . signal ( signal . SIGTERM , s i g n a l _ h a n d l e r )
92
93# Create p r o c e s s e s
94l e a r n e r _ p r o c e s s = mp . Process (
95target = run_learner ,
96args =(
97t r a n s i t i o n s _ q u e u e ,
98p ar ame te rs _q ueu e ,
99shutdown_event ,
100policy_learner ,
101o n l i n e _ r e p l a y _ b u f f e r ,
102o f f l i n e _ r e p l a y _ b u f f e r ,
103) ,
104kwargs ={ " device " : device } , # can run on a c c e l e r a t e d ha rd war e for t ra ini ng
105)
106
107a c t o r _ p r o c e s s = mp . Process (
108target = run_actor ,
109args =(
110t r a n s i t i o n s _ q u e u e ,
111p ara me te rs _q ueu e ,
112shutdown_event ,
113policy_actor ,
114r e w a r d _ c l a s s i f i e r ,
115env_cfg ,
116o utp ut _d ir ec tor y ,
117) ,
118kwargs ={ " device " : " cpu " } , # actor is frozen , can run on CPU or a c c e l e r a t e for i n f e r e n c e
119)
120
121l e a r n e r _ p r o c e s s . start ()
122a c t o r _ p r o c e s s . start ()
123
124try :
125# Wait for actor to finish ( it c on tro ls the episode loop )
126a c t o r _ p r o c e s s . join ()
127s h u t d o w n _ e v e n t . set ()
128l e a r n e r _ p r o c e s s . join ( timeout =10)
129
31

[PAGE 32]

130except K e y b o a r d I n t e r r u p t :
131print ( " Main process i n t e r r u p t e d " )
132s h u t d o w n _ e v e n t . set ()
133a c t o r _ p r o c e s s . join ( timeout =5)
134l e a r n e r _ p r o c e s s . join ( timeout =10)
135
136finally :
137if l e a r n e r _ p r o c e s s . is_ al iv e ():
138l e a r n e r _ p r o c e s s . t e r m i n a t e ()
139if a c t o r _ p r o c e s s . i s_a li ve ():
140a c t o r _ p r o c e s s . t e r m i n a t e ()
3.2.2 Limitations of RL in Real-World Robotics: Simulators and Reward Design
Despite the advancements in real-world RL training, training RL agents for real-world tasks still suffers from the
following limitations:
• In those instances where real-world training experience is prohibitively expensive to gather (e.g., Tokamak
control (Degrave et al., 2022), Autonomous Stratospehere Navigation (Bellemare et al., 2020))in-simulation training
is often the only viable option. However, high-fidelity simulators for real-world problems can be difficult to build
and maintain, especially for contact-rich manipulation and tasks involving deformable or soft materials.
• Reward design is a fundamental source of brittleness in real-world RL pipelines. While shaping dense rewards
is often necessary to guide exploration in long-horizon tasks, the process is error-prone and heavily reliant on
human expertise and intuition. Poorly tuned terms can lead to specification gaming or convergence to local optima,
making reward shaping a critical challenge for applying RL in practice. Sparse rewards that only signal successful
trajectories can avoid these pitfalls but typically result in much slower learning due to reduced supervision.
Advances in learning to act from potentially large corpora of human demonstrations via Behavioral Cloning (BC)
address both of these concerns. Although suffering from an inherent suboptimality—imitation learning can at most
match the performance level of the demonstrator—learning to reproduce expert demonstrations via BC has proven
increasingly competitive and practical, bypassing the need for simulated environments and hard-to-define reward
functions.
32

[PAGE 33]

Figure 18 | (A) Average (with standard deviation) evolution of the actuation levels over the first 5 recorded episodes in
lerobot/svla_so101_pickplace. Proprioperceptive states provide invaluable to determine the robot’s state during an episode.
(B) Camera frames are also recorded alongside measurements on the robot’s state, capturing information about the robot’s
interaction with its environment.
4 Robot (Imitation) Learning
The best material model for a cat
is another, or preferably the same
cat
Norbert Wiener
TL;DR
Behavioral Cloning provides a natural platform to learn from real-world interactions without the need to
design any reward function, and generative models prove more effective than point-wise policies at dealing with
multimodal demonstration datasets.
Learning from human demonstrations provides a pragmatic alternative to the RL pipeline discussed in Section 3.
Indeed, especially in real-world robotics, online exploration is typically costly and potentially unsafe, and designing
(dense) reward signals is a brittle and task-specific process. Further, even success detection itself often requires bespoke
instrumentation, while episodic training demands reliable resets—all factors complicating training RL algorithms
on hardware at scale. Behavioral Cloning (BC) sidesteps these constraints by casting control an imitation learning
problem, leveraging previously collected expert demonstrations to anchor the learned autonomous behavior. Most
notably, bylearning-to-imitate, autonomous systems naturally adhere to the objectives, preferences, and success
criteria implicitly encoded in the data, which reduces early-stage exploratory failures and obviates hand-crafted reward
shaping altogether.
Formally, letD ={τ (i)}N
i=1 be a set of expert trajectories, withτ (i) ={(o(i)
t ,a (i)
t )}Ti
t=0 representing thei-th length-Ti
trajectory inD, ot∈O denoting observations (e.g., images and proprioception altogether), andat∈A the expert
actions. Typically, observationso∈O consist of both image and proprioperceptive information, while actionsa∈A
represent control specifications for the robot to execute, e.g. a joint configuration. Note that differently from Section 3,
in the imitation learning contextD denotes an offline dataset collectingN length-Ti reward-free (expert) human
trajectories τ (i), andnotthe environment dynamics. Similarily, in this sectionτ (i) represent a length-Ti trajectory
of observation-action pairs, which cruciallyomits entirely any rewardinformation. Figure 18 graphically shows
trajectories in terms of the average evolution of the actuation on the 6 joints of a teleoperated SO-100 manipulator.
Notice how proprioperceptive states are captured jointly with camera frames over the course of the recorded episodes,
providing a unified high-frame rate collection of both image and joint teleoperation data. Figure 19 shows(ot,at)-pairs
for the same dataset, with the actions performed by the human expert illustrated alongside the corresponding
observation. In principle, (expert) trajectoriesτ (i) can have different lengths since demonstrations might exhibit
multi-modal strategies to attain the same goal, resulting in multiple, different behaviors.
Behavioral Cloning (BC) (Pomerleau, 1988) aims at producing synthetic behaviors by learning the mapping from
33

[PAGE 34]

Figure 19 | Sample observations and action pairs over the course of a given trajectory recorded inlerobot/svla_so101_
pickplace. Observations, comprising of both proprioperceptive and visual information, are recorded alongside the configuration
of a second, leader robot controlled by a human expert, providing complete information for regressing actions given observations.
observations to actions, and in its most natural formulation can be effectively tackled as asupevisedlearning problem,
consisting of learning the (deterministic) mappingf:O7→A, a t =f(o t)by solving
min
f
E(ot,at)∼p(•)L(at,f(o t)),(18)
given an arbitrary risk functionL:A×A7→R,L(a,a ′).
Typically, the expert’s joint observation-action distributionp :O×A7→ [0, 1]is assumed to be unknown, in keeping
with a classic Supervised Learning (SL) framework3. However, differently from standard SL assumptions, the samples
collected inD—realizations of the underlyingp—arenoti.i.d., as expert demonstrations are collectedsequentiallyin
the form of trajectories. In practice, this aspect can be partially mitigated by considering pairs in a non-sequential
order—shufflingthe samples in D—so that the expected risk underp can be approximated using MC estimates,
although these estimates may in general be less accurate. Another strategy to mitigate the impact of regressing
over non-i.i.d. samples relies on the possibility of interleaving BC and data collection (Ross et al., 2011, DAgger),
aggregating multiple datasets iteratively. However, because we only consider the case where a single offline datasetD
of trajectories is available and no more data can be collected, DAgger falls out of our scope.
Despite the inherent challenges of learning from non-i.i.d. data, the BC formulation presents several operational
advantages in robotics. First, training happens offline and naturally accomodates for expert, demonstration data,
hereby severily limiting exploration risks by preventing the robot from performing dangerous actions altogether,
by anchoring action in imitation. Second, reward design is entirely unnecessary in BC, as demonstrations already
reflect human intent. The absence of rewards also prevents the risk of misalignment and specification gaming (reward
hacking), otherwise inherent in purely reward-based RL (Heess et al., 2017). Third, because expert trajectories encode
terminal conditions, success detection and resets are implicit in the dataset. Finally, empirical evidence suggests the
performance of BC scales naturally with growing corpora of demonstrations collected across tasks, embodiments, and
environments. Nonetheless, BC can, in principle, only reproduce behaviors that are at best as good as those of the
demonstrator, and therefore offers no remedy for the suboptimal decisions that humans may enact. This limitation is
particularly problematic in sequential decision-making tasks where expert demonstrations are scarce–—either because
data collection is costly or because human performance is inherently suboptimal. Yet, many robotics applications still
benefit from relatively inexpensive pipelines for collecting high-quality human-generated trajectories, justifying the
use of BC in such settings.
While conceptually elegant,point-estimate policies f :O7→A learned by solving eq. 18 have been observed to
suffer from (1) compounding errors (Ross et al., 2011) and (2) poor fit to multimodal distributions (Florence et al.,
2022; Ke et al., 2020). Figure 20 illustrates these two key issues related to learningexplicit policies(Florence
et al., 2022). Besides sequentiality inD, compounding errors due tocovariate shiftmay also prove catastrophic,
as even smallϵ-prediction errors0 <∥µ (ot)−at∥≤ϵ can quickly drive the policy into out-of-distribution states,
incuring in less confident generations and thus compounding errors (Figure 20, left). Moreover, point-estimate policies
typically fail to learnmultimodaltargets, which are very common in human demonstrations solving real-world robotics
problems, as multiple trajectories can be equally as good towards the accomplishment of a goal (e.g., symmetric
grasps, Figure 20, right). In particular, unimodal regressors tend to average across modes, yielding indecisive or
3Throughout, we will adopt the terminology and notation for SL used in Shalev-Shwartz and Ben-David (2014)
34

[PAGE 35]

Figure 20 | Point-wise policies suffer from limitations due to (A) covariate shifts and (B) poor approximation of multimodal
demonstrations. (A) Small errors may drive the policy out of distribution, incuring in a vicious circle ultimately resulting in
failure. (B) Both modes of reaching for a target object in the scene—either left or right-first—are equally as good and thus
equally as likely to be present in a dataset of human demonstrations, ultimately resulting in multimodal demonstrations.
Figure 21 | Intuitively, latent variable in a single latent model may contain information regarding the task being performed,
which directly results in the likelihood of the same observation-action pair being different for two different tasks. When (A)
picking a block the likelihood of a wide gripper’s opening should be higher than narrower one, while it should be the opposite
when (B) pushing the block.
even unsafe commands (Florence et al., 2022). To address poor multimodal fitting, Florence et al. (2022) propose
learning thegenerative modelp(o,a )underlying the samples inD, rather than explicitly learning a prediction function
f:a=f(o).
4.1 A (Concise) Introduction to Generative Models
Generative Models (GMs) aim to learn the stochastic process underlying the very generation of the data collected, and
typically do so by fitting a probability distribution that approximates the unknowndata distribution,p. In keeping
with the GM literature,p(x)←P (x),x∼p . In the case of BC, the unknown data distributionp may represent
the expert’s joint distribution over(o,a )-pairs. Thus, given a finite set ofN pairsD ={(o,a )i}N
i=0 available as an
imitation learning target (and thus assumed to be i.i.d.), GMs seek to learn aparametricdistributionpθ(o,a )such
that (1) new samples(o,a )∼p θ(•)resemble those stored inD, and (2) high likelihood is assigned to theobserved
regions of theunobservable p. Likelihood-based learning provides a principled training objective to achieve both goals,
and it is thus extensively used in GMs (Prince, 2023).
35

[PAGE 36]

Figure 22 | (A) The latent variable model in a robotics application regulates influence between observed (o,a )variables and
an unobservable latent variable. (B) VAEs approximate exact latent variable models by means of variational inference.
4.1.1 Variational Auto-Encoders
A common inductive bias used in GM posits samples(o,a )are influenced from an unobservable latent variablez∈Z ,
resulting in:
p(o,a) =
Z
supp(Z)
p(o,a|z)p(z)(19)
Intuitively, in the case of observation-action pairs(o,a )for a robotics application,z could be interpreted as some high
level representation of the underlying task being performed by the human demonstrator. In such case, treatingp(o,a )
as a marginalization oversupp(Z)of the complete joint distributionp(o,a,z )natively captures the effect different
tasks have on the likelihood of observation-action pairs. Figure 21 graphically illustrates this concept in the case of a
(A) picking and (B) pushing task, for which, nearing the target object, the likelihood of actions resulting in opening
the gripper—the higherq6, the wider the gripper’s opening—should intuitively be (A) high or (B) low, depending
on the task performed. While the latent spaceZ typically has a much richer structure than the set of all actual
tasks performed, eq. 19 still provides a solid framework to learn joint distribution conditioned on unobservable yet
relevant factors. Figure 22 represents this latent-variable framework in the context of a robotics application: the true,
z-conditioned generative process assignslikelihoodp((o,a )|z)to the single( o,a )-pair. Using Bayes’ theorem, one can
reconstruct theposteriordistribution on supp(Z), qθ(z|o,a )from the likelihood pθ(o,a|z ),prior pθ(z)andevidence
pθ(o,a ). VAEs approximate the latent variable model presented in eq. 19 using anapproximate posteriorqϕ(z|o,a )
while regressing parameters for a parametric likelihood,pθ(o,a|z)(Figure 22).
Given a datasetD consisting ofN i.i.d. observation-action pairs, the log-likelihood of all datapoints underθ (in
Bayesian terms, theevidencep θ(D)) can be written as:
logpθ(D) = log
NX
i=0
pθ((o,a)i)(20)
= log
NX
i=0
Z
supp(Z)
pθ((o,a)i|z)p(z)(21)
= log
NX
i=0
Z
supp(Z)
qθ(z|(o,a)i)
qθ(z|(o,a)i)·pθ((o,a)i|z)p(z)(22)
= log
NX
i=0
Ez∼qθ(•|(o,a)i)
 p(z)
qθ(z|(o,a)i)·pθ((o,a)i|z)

,(23)
where we used eq. 19 in eq. 20, multiplied by1 =qθ(z|(o,a)i)
qθ(z|(o,a)i) in eq. 21, and used the definition of expected value in
eq. 23.
In the special case where one assumes distributions to be tractable,pθ(D)is typically tractable too, andmaxθ logpθ(D)
provides a natural target for (point-wise) infering the unknown parametersθ of the generative model. Unfortunately,
eq. 23 is rarely tractable when the distributionp is modeled with approximators such as neural networks, especially
for high-dimensional, unstructured data.
In their seminal work on Variational Auto-Encoders (VAEs), Kingma and Welling (2013) present two major contribu-
tions to learn complex latent-variable GMs from unstructured data, proposing (1) a tractable, variational lower-bound
36

[PAGE 37]

to eq. 23 as an optimization target to jointly learn likelihood and posterior and (2) using high-capacity function
approximators to model the likelihoodpθ(o,a|z)and (approximate) posterior distributionq ϕ(z|o,a)≈q θ(z|o,a).
In particular, the lower bound on eq. 23 (Evidence LOwer Bound,ELBO) can be derived from eq. 23 applying
Jensen’s inequality—logE[•]≥E[log(•)]—yielding:
logpθ(D)≥
NX
i=0

Ez∼qθ(•|(o,a)i)

logpθ((o,a)i|z)

+Ez∼qθ(•|(o,a)i)

log
 p(z)
qθ(z|(o,a)i)

(24)
=
NX
i=0
 
Ez∼qθ(•|(o,a)i)

logpθ((o,a)i|z)

−D KL

qθ(z|(o,a)i)∥p(z)

(25)
The true, generally intractable, posteriorqθ(z|o,a )prevents computing both the expectation and KL divergence
terms in eq. 25, and therefore Kingma and Welling (2013) propose deriving the ELBO using anapproximateposterior
qϕ(z|o,a), resulting in the final, tractable, ELBO objective,
ELBOD(θ,ϕ) =
NX
i=0
 
Ez∼qϕ(•|(o,a)i)

logpθ((o,a)i|z)

−D KL

qϕ(z|(o,a)i)∥p(z)

(26)
From Jensen’s inequality, maximizing ELBO results in maximizing the log-likelihood of the data too, thus providing a
natural, tractable optimization target. Indeed, expectations can be estimated using MC estimates from the learned
distributions in eq. 26, while the KL-divergence term can typically be computed in closed-form (1) modelingqϕ as a
Gaussian qϕ(z|o,a ) =N
 
µϕ(o,a ), Σϕ(o,a )

with learned mean vectorµϕ(o,a )and learned variance-covariance matrix
Σϕ(o,a)and (2) imposing a standard Gaussian prior on the latent space,p(z) =N(0,I).
An intuitive explanation of the learning dynamics of VAEs can be given considering the equivalent case ofminimizing
the negative ELBO, which admits the particularly interpretable factorization (considering, without loss of generality,
only one(o,a)∼D):
min
θ,ϕ
−ELBO(o,a)∼D(θ,ϕ) = min
θ,ϕ
Lrec(θ) +Lreg(ϕ),(27)
Lrec(θ) =E z∼qϕ(•|o,a)

logpθ(o,a|z)

(28)
Lreg(ϕ) =D KL

qϕ(z|o,a)∥p(z)

.(29)
For any given(o,a)pair, the expected value term in eq. 28 is typically computed via MC estimates, resulting in
−Ez∼qϕ(•|o,a)

logpθ(o,a|z)

=L rec≈− 1
n
nX
i=0
logpθ(o,a|zi).
Assuming pθ(o,a|z )to be parametrized with an isotropic Gaussian distribution with meanµθ(z)∈R d and variance
σ2, the log-likelihood thus simplifies to:
logp(o,a|z i) =− 1
2σ2
(o,a)−µ θ(zi)
2
2− d
2 log(2πσ2) =⇒L rec≈ 1
n
nX
i=0
(o,a)−µ θ(zi)
2
2
In practice, it is common to approximate the learned likelihoodpθ(o,a|z )with a parametric distribution (e.g.,
Gaussian) whose parameters are given by a learned coefficient vector derived fromµθ(z), z∼p (•). Under this
formulation, learning a VAE amounts to (1)reconstructingthe examples inD by minimizing (1) the reconstruction
loss Lrec—a standardsupervised learningobjective for regression—while (2)regularizingthe latent representation by
minimizing Lreg. The latter enforces information compression, since with the common prior choicep(z) =N (0, I)in
eq. 29, the regularizer constrains the posterior and thereby limits the expressivity ofqϕ(z|o,a).
4.1.2 Diffusion Models
VAEs approximate probability distributions via asinglelatent variable model, assuming the underlying unknown
distribution can be factored according to eq. 19, and solve the variational-inference problem of jointly learning
the likelihoodpθ and (approximate) posteriorqϕ for such model. In that, the unknown data distributionp(o,a )is
effectively approximated via
R
Zp(z)pθ(o,a|z ), and the underlying generative process reproduced by (1) sampling a
37

[PAGE 38]

Figure 23 | HMLV models posit the data generation process is influenced by a stack of Markov-dependent latent variables,
with samples from the posterior distribution being progressively higher up in the hierarchy.
latent variable and (2) learning to decode it into a high-likelihood sample under the (unknown)p(o,a ). Diffusion
Models (DMs) (Ho et al., 2020) are another class of GMs which treat the similar problem of approximating an
underlying unknown data distribution—variational inference—bypartiallyextending VAEs to the case wheremultiple
latent variables influence each other and the generative process underlyingo,a itself. In particular, DMs posit the
generative process can be decomposed to a series of piece-wise (Markovian) interactions between (latent) variables
(Figure 23), resulting in
p(o,a|{z}
=z0
) =
Z
supp(Z0)
Z
supp(Z1)
...
Z
supp(ZT )
p(z0,z 1,...z T )(30)
p(z0,z 1,...z T ) =p(z T )
TY
t=1
p(zt−1|zt),(31)
where we explicitly showed the marginalization over the multiple latents in eq. 30, and used the law of conditional
probability and Markov property in eq. 31. Also, for ease of notation, we will refer to observation-action pairso,a as
z0.
Similar to VAEs, it is generally not possible to assign anexactinterpretation to the latent variables. Nevertheless, a
reasonable application-driven intuition is that Hierarchical Markov Latent Variable (HMLV) models, by capturing
hierarchical and decoupled interactions among latent variables, can reflect the different resolutions at which conditioning
factors intervene. For example, in a robotics setting, one might naturally distinguish between high-level trajectory
planning (higher up in the hierarchy,t→T ) and fine-grained motion adjustments (closer to empirical observations,
t→ 0). In that, HMLV models thus provide a framework to perform variational inference via multiple, sequential
sampling steps from different higher level distributions instead of approximating the generative process with a
single-latent variable model. DMs are a particular instantiation of HMLV models for which the posterior is fixed to
q(zt|zt−1) =N (zt
√1−β t,βtI), for a givenβt∈R +. In practice,βt is used to iteratively reduce the signal-to-noise
ratio along the latents’ hierarchy, similarily to how a diffusion process influences the information of a physical system.
Just like VAEs, DMs attemp to learn to reproduce an underlying data distributionp(o,a )given a collection of
i.i.d. samples approximating the model posited to have generated the data in the first place (eq. 30). Similarily to
VAEs, DMs approximate the process of sampling from the unknownp(o,a)by (1) sampling from an easy-to-sample
distribution (e.g., Gaussian) and (2) learning to reconstruct high-likelihood samples under the unknown distribution.
However, in stark contrast with VAEs, the easy-to-sample distribution containsno mutual informationregarding the
data distributionp(o,a ). Crucially, as no information from the sample(o,a )(denoted as z0≡ (o,a )for simplicity of
notation) is assumed to be propagated throughout the chain of latents, the posteriorq(zt|zt−1)assumes a relatively
amicable structure in DMs, reducing complexity. Thetruelikelihoodp(zt−1|zt)is instead typically approximated using
the parametrizationpθ(zt−1|zt). In that, the information contained in the unknwon data distribution isreconstructed
via a process in which samples from a fixed distribution are iteratively turned into (ideally) high-likelihood samples
underp(o,a)—a process referred to asdenoising.
38

[PAGE 39]

Under such model, we can express the log-likelihood of an arbitrary samplez0 as:
logpθ(z0) = log
Z
supp(Z1)×supp(Z2)×···×supp(ZT )
pθ(z0,z 1,z 2,...z T| {z }
z0:T
)(32)
= log
Z
supp(Z1:T )
pθ(z0:T )·q(z 1:T|z0)
q(z1:T|z0) (33)
= logEz1:T∼q(•|z0)
 pθ(z0:T )
q(z1:T|z0)

(34)
≥E z1:T∼q(•|z0)

log pθ(z0:T )
q(z1:T|z0)

(35)
=E z1:T∼q(•|z0)

logp(zT )QT
t=1pθ(zt−1|zt)
QT
t=1q(zt|zt−1)

(36)
=E z1:T∼q(•|z0)

logp(zT )·p θ(z0|z1)QT
t=2pθ(zt−1|zt)
q(zT|zT−1 )QT−1
t=1 q(zt|zt−1)

(37)
=E z1:T∼q(•|z0)

logp(zT )·p θ(z0|z1)QT−1
t=1 pθ(zt|zt+1)
q(zT|zT−1 )QT−1
t=1 q(zt|zt−1)

(38)
=E z1:T∼q(•|z0)

logp(zT )·p θ(z0|z1)
q(zt|zt−1)

+Ez1:T∼q(•|z0)

log
T−1Y
t=1
pθ(zt|zt+1)
q(zt|zt−1)

(39)
=E z1:T∼q(•|z0)

logpθ(z0|z1)

+Ez1:T∼q(•|z0)

log p(zT )
q(zT|zT−1 )

+
T−1X
t=1
Ez1:T∼q(•|z0)

logpθ(zt|zt+1)
q(zt|zt−1)

(40)
=E z1∼q(•|z0)

logpθ(z0|z1)

+EzT−1:T∼q(•|z0)

log p(zT )
q(zT|zT−1 )

+
T−1X
t=1
Ezt−1:t+1∼q(•|z0)

logpθ(zt|zt+1)
q(zt|zt−1)

(41)
=E z1∼q(•|z0) logpθ(z0|z1)−E zT−1∼q(•|z0)

DKL(q(zT|zT−1 )∥p(zT ))

(42)
−
T−1X
t=1
E(zt−1,zt+1)∼q(•|z0)

DKL(q(zt|zt−1)∥pθ(zt|zt+1))

,
where we: used eq. 30 and multiplied by1 =q(z1:T|z0)
q(z1:T|z0) in eq. 33; used Jensen’s inequality in eq. 35; used the law of
conditional probability for both numerator and denominator in eq. 36; stepped forward and backward the products in
the numerator and denominator products in eq. 37, respectively; reindexed the product terms in eq. 38; removed
out-of-expectation variables in eq. 41; used the defintion of KL-divergence in eq. 42. In turn, eq. 42 provides an
optimization target tolearnp θ solvingmax θ logpθ(D).
In their seminal work on using DMs for variational inference, Ho et al. (2020) introduce major contributions regarding
solving minθ−logp θ(z0). In particular, Ho et al. (2020) exclusively adopt afixed, isotropic Gaussian posterior
in the form ofq(zt|zt−1) = N (√1−β tzt−1,βtI). The choice of adopting Gaussians has profound implications
on the generative process modeled. Indeed, under the (mild) assumption that the variance is sufficiently small
βt≤η,η∈R +, Sohn et al. (2015) proved that the likelihoodp(zt−1|zt)is Gaussian as well, which allows for the
particularly convenient parametrization of the approximate likelihoodpθ(zt−1|zt) =N (µθ(zt,t ), Σθ(zt,t )), t∈ [1,T ],
as well as for closed-form tractability of the KL-divergence terms in eq. 42. Further, the posterior’s structure also
enables the analytical description of the distribution of thet-th latent variable,q(zt|z0) =N (√¯αtz0, (1−¯αt)I), with
αt = 1−βt,¯αt =Qt
k=1αk, conveniently preventing iterative posterior sampling simplifying computing eq. 42. It
follows:
∇θ logpθ(z0) =E z1∼q(•|z0)∇θ logpθ(z0|z1)−
T−1X
t=1
Ezt−1,zt+1∼q(•|z0)∇θDKL(q(zt|zt−1)∥pθ(zt|zt+1),(43)
where the former term is equivalent to the reconstruction term in eq. 27 and the latter term can be obtained in closed
form.
Besides mathematical tractability of eq. 43, adopting Gaussian posteriors allows for a particularly intuitive inter-
pretation of the training dynamics of DMs (Permenter and Yuan, 2024). As the hierarchical latent variables are
39

[PAGE 40]

Figure 24 | DMs iteratively corrupt samples (left) from an unknown distribution into a quasi-standard Gaussian (center),
learning the displacement field (right) that permits to reconstruct samples from the unknown target distribution by iteratively
denoising samples of a tractable, easy-to-sample distribution.
40

[PAGE 41]

Figure 25 | A joint action-observation distribution, in the simplified case where the observation is the elbow-flex actuation in
a SO-100, and the action is the recorded position for the same joint from the teleoperator arm. The motion recorded being
teleoperated, the points distribute along a the diagonal.
repeatedly corrupted by applying increasingly more Gaussian noise, they progressively lose information about the
original (unknown) samplez0, converging toward a standard Gaussian which eventually contains no information at all
(Figure 24). Figure 24 illustrates this process on a simplified, bidimensional observation-action distribution, where we
considered o =q2 and a =qh
2, withq2 denoting the robot’selbow flexactuation and qh
2 the corresponding human
teleoperator’s elbow flex. Because the recorded behavior is teleoperated, measurements mostly distribute along the
line a =o +η,η∼N (0, 1), withη-variability accouting for minor control inconsistencies (Figure 25). Notice how
corrupted samples distribute differently from the most reasonable structurea≃o , further underscoring how diffusion
corrupts both the individual samples and the global distribution (Figure 24, left and center). In this, using Gaussian
posteriors—i.e., adding Gaussian noise—effectively simulates aBrownian motionfor the elements in the distribution’s
support (in Figure 24,O×A ), whereby informationdiffuses awayfrom the samples. Comparing the diffused samples
to the original data points, one can derive an estimate of the total displacement induced by the diffusion process,
and, under the assumption that the likelihood of the totally diffused samples is low under the original unknown data
distribution, one can effectively approximate the unkwown distribution bylearning to reversesuch displacement. This
key intuition allows to write a simplified training objective4:
L(θ) =E t,z0,ϵ

∥ϵ−ϵ θ(√¯αtz0 +ϵ
√
1−¯αt,t)∥ 2
, t∼U({1,...,T}), z 0∼D, ϵ∼N(0,I).(44)
In this simplified (minimization) objective, the optimization process differs from eq. 42 in that, rather than maximizing
pθ directly, the parametersθ of the pairwise likelihoodpθ(zt−1|zt)are adjusted topredict the total displacementϵ for
a randomly long (t∼U({1,...,T})) diffusion process starting from a sample of the target distribution.
By learning the total displacement from a generally, uninformative corrupted sample obtained diffusing information
and a sample from an unknown distribution Ho et al. (2020) show that one can approximate the underlying distribution
reversing the displacement,denoisingsamples. Interestingly, under the hypothesis that real-world data belongs to a
single, higher-dimensional manifold (Manifold Hypothesis), Permenter and Yuan (2024) show that diffusion learns the
gradient of a distance function from any off-point manifold (such as perturbed, uniformative samples), and the data
manifold itself. Following this gradient—i.e., denoising a sample from an uninformative distribution—corresponds to
projecting back into the manifold, yielding a procedure to sample from unknown distributions by means of Euclidean
projection. Indeed, under the assumption thatpθ(zt−1|zt)is Gaussian, sampling zt−1∼p θ(•|zt)corresponds to
computing:
zt−1 = 1√αt

zt− βt√1−¯αt
ϵθ(zt,t)

+σtϵ, ϵ∼N(0,I),(45)
thus showing that the lower-level latent variables in a DM can be obtained by iteratively removing noise from the
one-step higher order variable, using the noise regressorϵθ(zt,t)learned minimizing eq. 44.
4.1.3 Flow Matching
The posterior parametrization adopted by DMs proved traditionally effective, yet it raised concerns circa itsefficiency
at inference time, where a possibly large number (hundreds) of compute-expensive denoising steps are needed in
order to recover a sample from the target distribution. Flow Matching (FM) (Lipman et al., 2023) extends DMs
4See Luo (2022, "Three equivalent interpretations") for a complete derivation
41

[PAGE 42]

Figure 26 | Probability distributions can be modified differently by applying different vector fields, inducing different
flows of mass across the same support (top versus bottom, using two different time-invariant 2D-fieldsu1(x,y ) = (x, 0)and
u2(x,y ) = (x/
√
2,y/
√
2)). Notice time flowscontinuouslyin[0 , 1]. FM models learn to approximate a target vector field,
thereby producing arbitrary (goal) transformations of an easy-to-sample initial distribution.
to the general case of arbitrary likelihood and posteriors, and in this defines a superseding class of GMs providing
a unified framework for learningcontinuous transformationsbetween distributions, encompassing and generalizing
DMs. Instead of astochastic, discrete, multi-stepdenoising process, FM aims to learn adeterministic, continuous,
differentiable flowψ : [0, 1]×Z7→Z , formalized starting from a (possibly time-dependent) vector fieldv : [0, 1]×Z7→Z
transporting over timesamples from a simple prior distributionp0—e.g., a standard Gaussian—to a more complex,
typically unknown data distributionp1. In this, FM accomodates for arbitrary intermediate distributions, breaking
free from the particular case where posterior and likelihood are exclusively Gaussians. Note also how FM models time
t∈ [0, 1]to be varying continuously while moving awayfroman easy-to-sample distributionp0 towardsthe unknown
data-distribution, p1. This results in a continuous (and deterministic) trajectory at inference, which is in practice
more efficient compared to following stochastic paths like in DMs. Formally, FM can be fully characterized by an
ordinary differential equation (ODE) relating instantaneous variations of flows with the underlying vector field, and
hence providing complete trajectories over the distributions’ support when integrating over time,
d
dtψ(z,t) =v(t,ψ(t,z)),(46)
ψ(0,z) =z.(47)
In practice, flow models learn to approximate these dynamics by estimating a vector fieldv that matches the true,
unknownu, so that the induced flowsψcan approximate the ideal trajectoriesψ∗.
FM proved very effective in a variety of applications, ranging from image (Esser et al., 2024) and video genera-
tion (Polyak et al., 2025) to robotics control (Black et al., 2024). Most notably, in their introductory work on FM for
GM, Lipman et al. (2023) show how DMs can be seen as a specific instance of FM where theconditionaltarget vector
fieldvlearned by the noise regressorε θ corresponds to:
u(t,z|z 0) =
d
dtα(1−t)
1−(α(1−t)) 2 (α(1−t)z−z 0), α(t) =e − 1
2
Rt
0 β(s)ds,∀z 0∈D.(48)
Conditional vector fields are defined not only over their argumentz and timet, but do also vary with respect to an
auxiliary variablez0, thereby extending the standard notion of a vector field to incorporate additional conditioning.
Note that the traditional discrete-time noise-scheduler{βt}T
t=0 is now generalized to a continuous mapβ : [0, 1]7→R +.
Crucially, Lipman et al. (2023) prove that by exclusively optimizing the vector field for individual data pointsz0∈D ,
one also retrieves the optimal flow to morph the entire support of the initial distributionp0 intop 1 s.t.D∼p 1.
While the noising schedule of DMs results in a stochastic resembling a random (Brownian) walk, FM allows for more
general—potentially, deterministic—likelihood and posterior parametrization. In the FM literature the likelihood and
posterior probabilty densities defined along a HMLV model are typically referred to as aprobability path, where the
distributions for successive adjacent transitions in the HMLV model are related by the (normalized) flow between them
(Figure 26). The inherent flexibility of FM is one of their key advantages over DMs, as it opens up the possibility of
42

[PAGE 43]

Figure 27 | Compared to diffusion, flow matching distorts distribution along a less randomic pattern, resulting in a clearer
interpolation between source and target distribution. The visualization shows an example comparison between these two
methods on joint distribution of robot observations and actions overT= 50steps.
learningmore efficient paths. For instance, one can design probability paths inspired by Optimal Transport (OT), a
mathematical framework concerned with characterizing the most efficient morphings between probability distributions.
Probability paths obtained through OT paths tend to bestraighterthan diffusion paths (Figure 27), which can lead
to faster and more stable training, as well as empirically result in higher-quality generations with fewer denoising
steps at inference time. In particular, by avoiding unnecessary backtracking associated with the inherent stochastic
nature of both the noising and denoising process in DMs, test-time compute is typically significantly reduced in FM,
while retaining comparable results (Lipman et al., 2023).
In practice, FM can be applied to generative modeling by learning a vector field regressorvθ(z,t )to approximate a
given target vector fieldu(t,z ). In the particular case of DMs,u(t,z )is defined as in eq. 48, while in priciple the
target vector field can be learned to induce an arbitrary mass displacement, or fixed according to OT. Given a sample
from the data distributionz1∼p 1 and a sample from an easy-to-sample priorz0∼p 0, Conditional FM (CFM) defines
a simple path between them usinglinear interpolationbetween sampleszt = (1−t )z0 +tz1, which in turn results in
the target vector fieldu(t,zt) =z1−z 0. FM models can then be trained with a simple regression objective defined as:
L(θ) =E t,z0,z1

∥vθ((1−t)z 0 +tz 1,t)−(z 1−z 0)∥2
, t∼U([0,1]),(49)
where z0∼p 0(•)and z1∼p 1(•). Note how in eq. 49—differently from eq. 44—time is assumed to be varying
continuously t∼U ([0, 1])rather than discretely t∼U ({0, ∆t, 2∆t,..., 1}), a key property of flow-based models.
Therefore, the objective in eq. 49 directly regresses the learned vector field onto the simple, straight path connecting
a point from the prior and a point from the data, providing a simulation-free training procedure that is both stable
and efficient. At inference time, samples are generated by starting withz0∼p 0 and iteratively refined according to
dz
dt =vθ(zt,t )for t∈ [0, 1]—an operation that can be numerically carried out with standard ODE solvers, and that in
practice is often carried out numerically via forward-Euler integrating over tens of denoising steps.
4.2 Action Chunking with Transformers
While GMs prove useful in learning complex, high-dimensional multi-modal distributions, they do not natively address
the compouding errors problem characteristic of modeling online, sequential predictions. In Action Chunking with
Transformers (ACT), Zhao et al. (2023) present an application of VAEs to the problem of learning purely from
offline trajectories, and introduce a simple, yet effective method to mitigate error compounding, learning high-fidelity
autonomous behaviors via BC. Drawing inspiration from how humans plan to enactsequencesof actionsat:t+k instead
of single actionsat, Zhao et al. (2023) propose learning a GM on a dataset of input demonstrations by modeling
chunksof multiple actions directly. Besides contributions to learning high-performance autonomous behaviors, Zhao
et al. (2023) also introduce hardware contributions in the form of a low-cost bimanual robot setup (ALOHA) capable
of performing fine-grained manipulation tasks, such as opening a lid, slotting a battery in its allotment or even prepare
tape for application. Notably, ALOHA bimanual setup costs just as much as a mono-arm Franka arm and can be
assembled from easy-to-source parts, underscoring its higher accessibility.
43

[PAGE 44]

Zhao et al. (2023) do also present significant algorithmic contributions related to synthetizing performant autonomous
behaviors for the ALOHA setup, adopting transformers as the architectural backbone to learn aConditionalVAE (Sohn
et al., 2015) from demonstrations. Conditional VAEs are a variation of the standard VAE introducing an arbitrary
conditioning on sampling from the latent prior, modelingone-to-manyrelationships between latent and data samples.
Further, in stark contrast with previous work (Florence et al., 2022; Janner et al., 2022), Zhao et al. (2023) do not
learn a full jointpθ(o,a )on observation and actions, and rather focus on the conditionalpθ(a|o). While thepolicy
distribution pθ(a|o)can in principle be entirely described from the jointpθ(o,a ), conditional distributions are often
intractable when using function approximators, aspθ(a|o) = pθ(o,a)R
Apθ(o,a), and the integral in the denominator is typically
intractable. Thus, instead of modeling the full joint using a vanilla VAE, Zhao et al. (2023) propose learning a
conditionalVAE (Sohn et al., 2015) modeling the policy distribution directly, hence approximatingp(a|o).
In practice, when learning from demonstrations adopting CVAEs results in a slight modification to the VAE objective
in eq. 26, which is adapted to:
ELBOD(θ,ϕ,ω) =
NX
i=0
 
Ez∼qϕ(·|oi,ai)

logpθ(ai|z,oi)

−D KL

qϕ(z|oi,ai)∥pω(z|oi)

(50)
Notice how in eq. 50 we are now also learning a new set of parametersω for the prior distribution in the latent space.
Effectively, this enables conditioning latent-space sampling (and thus reconstruction) during training (and potentially
inference too), providing useful when learning inherently conditional distributions like policies. Further, ACT is
trained as aβ-CVAE (Higgins et al., 2017), weighing the KL regularization term in eq. 50 with an hyperparameter
β∈R + regulating the information condensed in the latent space, wherehigherβ results in alessexpressive latent
space.
In their work, Zhao et al. (2023) ablated using a GM to learn from human demonstrations compared to a simpler,
supervised objective,L1(a,a′) =∥a−a ′∥1. Interestingly, they found the performance of these two approaches to be
comparable when learning fromscripteddemonstrations. That is, when learning from data collected rolling out a
predetermined set of commands[qc
0,qc
1,... ], GM didnotprove competitive compared to standard supervised learning.
However, when learning from human demonstrations—i.e., from data collected executing commands coming from a
human controller[qh
0,qh
1,... ]— Zhao et al. (2023) found performance (defined as the success rate on a downstream
task) to be severily (-33.3%) hindered from adopting a standard supervised learning objective compared to a richer,
potentially more complex to learn variational objective. The result of such ablation reflects from the multimodal
nature of human demonstrations data, and is consistent with the findings presented by Florence et al. (2022). The
authors also ablate the action chunking paradigm, reporting significant performance gains deriving from using action
chunking (1% vs. 44% success rate). To reduce acting open-loop, Zhao et al. (2023) also design an inference process
consisting in performing inference at every timestept and then aggregate multiple chunks using an exponential moving
average (EMA) on the overlapping chunks.
In ACT (Figure 30), inference for a given observationo∈O could be performed by (1) defining a priorpω(z|o)for
the latent variablez and (2) decoding an action chunk from a sampled latentz∼p ω(•|o), similarily to how sampling
from standard VAEs takes place, with the exception that vanilla VAEs typically posep(z|o)≡p (z)∼N (0, I)and
thus skip (1).
However, the authors claim that using a deterministic procedure to samplez benefits policy evaluation, and thus avoid
using the conditional prior at all at inference time, effectively using the CVAE framework exclusively to train a more
expressive decoder. At test time, Zhao et al. (2023) propose simply usingz =0, as the conditional prior onz used in
training is set to be a standard Gaussian. Further, conditioning on the observationo is achieved through explicitly
feeding proprioperceptive and visual observations to the decoder,pθ(a|z,o )at test time. If at inferencez is sampled
from a standard Gaussian, during trainingz is sampled from an approximate posterior distributionqϕ(z|o,a ), which,
however, disregards image observations and exclusively uses proprioperceptive states to formo for efficiency reasons.
44

[PAGE 45]

Figure 28 | The CVAE encoder used in ACT. Input action chunks are first embedded and aggregated with positional
embeddings, before being processed alongside embedded proprioperceptive information, and a learned[CLS] token used to
aggregate input level information, and predict the style variablez. The encoder is exclusively used totrainthe decoder, and it
is entirely disregarded at inference time.
Figure 29 | The CVAE decoder used in ACT, comprising of a full encoder-decoder Transformer architecture. Camera
observations from alln camera views are first embedded using pre-trained visual encoders, and then aggregated with the
corresponding positional embeddings. Then, the proprioperceptive information and style variablez retrieved from the CVAE
encoder, are fed to the encoder-decoder Transformer for inference. The encoder shares the matricesK,V with the decoder, and
is trained to decode fixed position embeddings into action chunks.
45

[PAGE 46]

Figure 30 | Action Chunking with Transformer (ACT), as in Zhao et al. (2023). ACT introduces an action chunking paradigm
to cope with high-dimensional multi-modal demonstration data, and a transformer-based CVAE architecture.
4.2.1 Code Example: Training and Using ACT in Practice
Code 7: Training ACT
https://github.com/fracapuano/robot-learning-tutorial/snippets/ch4/01_training_act.py
1from pathlib import Path
2
3import torch
4
5from lerobot . configs . types import F e a t u r e T y p e
6from lerobot . da ta set s . l e r o b o t _ d a t a s e t import LeRobotDataset , L e R o b o t D a t a s e t M e t a d a t a
7from lerobot . da ta set s . utils import d a t a s e t _ t o _ p o l i c y _ f e a t u r e s
8from lerobot . po li cie s . act . c o n f i g u r a t i o n _ a c t import A C T C o n f i g
9from lerobot . po li cie s . act . m o d e l i n g _ a c t import A C T P o l i c y
10from lerobot . po li cie s . factory import m a k e _ p r e _ p o s t _ p r o c e s s o r s
11
12
13def m a k e _ d e l t a _ t i m e s t a m p s ( d e l t a _ i n d i c e s : list [ int ] | None , fps : int ) -> list [ float ]:
14if d e l t a _ i n d i c e s is None :
15return [0]
16
17return [ i / fps for i in d e l t a _ i n d i c e s ]
18
19
20o u t p u t _ d i r e c t o r y = Path ( " outputs / r o b o t _ l e a r n i n g _ t u t o r i a l / act " )
21o u t p u t _ d i r e c t o r y . mkdir ( parents = True , ex is t_o k = True )
22
23# Select your device
24device = torch . device ( " mps " ) # or " cuda " or " cpu "
25
26d a t a s e t _ i d = " lerobot / s v l a _ s o 1 0 1 _ p i c k p l a c e "
27
28# This s p e c i f i e s the inputs the model will be e x p e c t i n g and the outputs it will produce
29d a t a s e t _ m e t a d a t a = L e R o b o t D a t a s e t M e t a d a t a ( d a t a s e t _ i d )
30f ea tu re s = d a t a s e t _ t o _ p o l i c y _ f e a t u r e s ( d a t a s e t _ m e t a d a t a . f ea tu res )
31
32o u t p u t _ f e a t u r e s = { key : ft for key , ft in fe atu re s . items () if ft . type is F e a t u r e T y p e . ACTION }
33i n p u t _ f e a t u r e s = { key : ft for key , ft in f ea tu re s . items () if key not in o u t p u t _ f e a t u r e s }
34
35cfg = A C T C o n f i g ( i n p u t _ f e a t u r e s = input_features , o u t p u t _ f e a t u r e s = o u t p u t _ f e a t u r e s )
36policy = A C T P o l i c y ( cfg )
37preprocessor , p o s t p r o c e s s o r = m a k e _ p r e _ p o s t _ p r o c e s s o r s (
46

[PAGE 47]

38cfg , d a t a s e t _ s t a t s = d a t a s e t _ m e t a d a t a . stats
39)
40
41policy . train ()
42policy . to ( device )
43
44# To perform action chunking , ACT expects a given number of actions as targets
45d e l t a _ t i m e s t a m p s = {
46" action " : m a k e _ d e l t a _ t i m e s t a m p s ( cfg . a c t i o n _ d e l t a _ i n d i c e s , d a t a s e t _ m e t a d a t a . fps ) ,
47}
48
49# add image fe atu re s if they are present
50d e l t a _ t i m e s t a m p s |= {
51k : m a k e _ d e l t a _ t i m e s t a m p s ( cfg . o b s e r v a t i o n _ d e l t a _ i n d i c e s , d a t a s e t _ m e t a d a t a . fps )
52for k in cfg . i m a g e _ f e a t u r e s
53}
54
55# I n s t a n t i a t e the dataset
56dataset = L e R o b o t D a t a s e t ( dataset_id , d e l t a _ t i m e s t a m p s = d e l t a _ t i m e s t a m p s )
57
58# Create the o p t i m i z e r and d a t a l o a d e r for offline tr ain in g
59o p t i m i z e r = cfg . g e t _ o p t i m i z e r _ p r e s e t (). build ( policy . p a r a m e t e r s ())
60b a t c h _ s i z e = 32
61d a t a l o a d e r = torch . utils . data . D a t a L o a d e r (
62dataset ,
63b a t c h _ s i z e = batch_size ,
64shuffle = True ,
65p i n _ m e m o r y = device . type != " cpu " ,
66d r o p _ l a s t = True ,
67)
68
69# Number of tr ain in g steps and logging f r e q u e n c y
70t r a i n i n g _ s t e p s = 1
71l og _f re q = 1
72
73# Run t rai ni ng loop
74step = 0
75done = False
76while not done :
77for batch in d a t a l o a d e r :
78batch = p r e p r o c e s s o r ( batch )
79loss , _ = policy . forward ( batch )
80loss . b ac kw ar d ()
81o p t i m i z e r . step ()
82o p t i m i z e r . z e r o _ g r a d ()
83
84if step % lo g_ fr eq == 0:
85print ( f " step : { step } loss : { loss . item ():.3 f } " )
86step += 1
87if step >= t r a i n i n g _ s t e p s :
88done = True
89break
90
91# Save the policy checkpoint , a l o n g s i d e the pre / post p r o c e s s o r s
92policy . s a v e _ p r e t r a i n e d ( o u t p u t _ d i r e c t o r y )
93p r e p r o c e s s o r . s a v e _ p r e t r a i n e d ( o u t p u t _ d i r e c t o r y )
94p o s t p r o c e s s o r . s a v e _ p r e t r a i n e d ( o u t p u t _ d i r e c t o r y )
95
96# Save all assets to the Hub
97policy . p u s h _ t o _ h u b ( " f r a c a p u a n o / r o b o t _ l e a r n i n g _ t u t o r i a l _ a c t _ e x a m p l e _ m o d e l " )
98p r e p r o c e s s o r . p u s h _ t o _ h u b ( " f r a c a p u a n o / r o b o t _ l e a r n i n g _ t u t o r i a l _ a c t _ e x a m p l e _ p i p e l i n e " )
99p o s t p r o c e s s o r . p u s h _ t o _ h u b ( " f r a c a p u a n o / r o b o t _ l e a r n i n g _ t u t o r i a l _ a c t _ e x a m p l e _ p i p e l i n e " )
47

[PAGE 48]

Code 8: Using ACT
https://github.com/fracapuano/robot-learning-tutorial/snippets/ch4/02_using_act.py
1import torch
2
3from lerobot . cameras . opencv . c o n f i g u r a t i o n _ o p e n c v import O p e n C V C a m e r a C o n f i g
4from lerobot . da ta set s . l e r o b o t _ d a t a s e t import L e R o b o t D a t a s e t M e t a d a t a
5from lerobot . po li cie s . act . m o d e l i n g _ a c t import A C T P o l i c y
6from lerobot . po li cie s . factory import m a k e _ p r e _ p o s t _ p r o c e s s o r s
7from lerobot . po li cie s . utils import b u i l d _ i n f e r e n c e _ f r a m e , m a k e _ r o b o t _ a c t i o n
8from lerobot . robots . s o 1 0 0 _ f o l l o w e r . c o n f i g _ s o 1 0 0 _ f o l l o w e r import S O 1 0 0 F o l l o w e r C o n f i g
9from lerobot . robots . s o 1 0 0 _ f o l l o w e r . s o 1 0 0 _ f o l l o w e r import S O 1 0 0 F o l l o w e r
10
11device = torch . device ( " mps " ) # or " cuda " or " cpu "
12m od el _i d = " f r a c a p u a n o / r o b o t _ l e a r n i n g _ t u t o r i a l _ a c t _ e x a m p l e _ m o d e l "
13model = A C T P o l i c y . f r o m _ p r e t r a i n e d ( m ode l_ id )
14
15d a t a s e t _ i d = " lerobot / s v l a _ s o 1 0 1 _ p i c k p l a c e "
16# This only d o w n l o a d s the m et ad ata for the dataset , ~10 s of MB even for large - scale da ta se ts
17d a t a s e t _ m e t a d a t a = L e R o b o t D a t a s e t M e t a d a t a ( d a t a s e t _ i d )
18preprocess , p o s t p r o c e s s = m a k e _ p r e _ p o s t _ p r o c e s s o r s (
19model . config , d a t a s e t _ s t a t s = d a t a s e t _ m e t a d a t a . stats
20)
21
22# # find ports using lerobot - find - port
23f o l l o w e r _ p o r t = ... # s o m e t h i n g like "/ dev / tty . u s b m o d e m 5 8 7 6 0 4 3 1 6 3 1 "
24
25# # the robot ids are used the load the right c a l i b r a t i o n files
26f o l l o w e r _ i d = ... # s o m e t h i n g like " f o l l o w e r _ s o 1 0 0 "
27
28M A X _ E P I S O D E S = 5
29M A X _ S T E P S _ P E R _ E P I S O D E = 20
30
31# Robot and e n v i r o n m e n t c o n f i g u r a t i o n
32# Camera keys must match the name and r e s o l u t i o n s of the ones used for t ra in in g !
33# You can check the camera keys e xpe ct ed by a model in the info . json card on the Hub
34c a m e r a _ c o n f i g = {
35" side " : O p e n C V C a m e r a C o n f i g ( i n d e x _ o r _ p a t h =1 , width =640 , height =480 , fps =30) ,
36" up " : O p e n C V C a m e r a C o n f i g ( i n d e x _ o r _ p a t h =1 , width =640 , height =480 , fps =30) ,
37}
38
39r o b o t _ c f g = S O 1 0 0 F o l l o w e r C o n f i g ( port = follower_port , id = follower_id , cameras = c a m e r a _ c o n f i g )
40robot = S O 1 0 0 F o l l o w e r ( r o b o t _ c f g )
41robot . connect ()
42
43for _ in range ( M A X _ E P I S O D E S ):
44for _ in range ( M A X _ S T E P S _ P E R _ E P I S O D E ):
45obs = robot . g e t _ o b s e r v a t i o n ()
46o b s _ f r a m e = b u i l d _ i n f e r e n c e _ f r a m e ( obs , d a t a s e t _ m e t a d a t a . features , device )
47
48obs = p r e p r o c e s s ( o b s _ f r a m e )
49
50action = model . s e l e c t _ a c t i o n ( obs )
51action = p o s t p r o c e s s ( action )
52
53action = m a k e _ r o b o t _ a c t i o n ( action , d a t a s e t _ m e t a d a t a . f ea tu re s )
54
55robot . s e n d _ a c t i o n ( action )
56
57print ( " Episode fi nis he d ! S ta rti ng new episode ... " )
4.3 Diffusion Policy
DMs have proven very effective in approximating complex highly dimensional distributions, such as distributions over
images (Ho et al., 2020) or videos (Polyak et al., 2025), thanks to their inherent capability to deal with multimodal
data, and their training stability. In Diffusion Policy (DP), Chi et al. (2024) present an application of DMs the
48

[PAGE 49]

Figure 31 | The Diffusion Policy archicture, as in Chi et al. (2024). A stack ofHo previous observations is used as external
conditioning to denoise a group ofHa actions. Conditioning is performed at every layer of a U-Net block. Diffusion Policy
allows to obtain fully-formed action chunks with as little asT= 10denoising steps.
field of robot learning, leveraging diffusion to model expert demonstrations in a variety of simulated and real-world
tasks. Similarily to ACT (Zhao et al., 2023), Chi et al. (2024) (1) adopt a modifiedobservation-conditioned target
distributioninstead of the full jointp(o,a ), and (2) predict multiple actions into the future instead of a single action.
Besides the intractability of the observations’ marginalpθ(o)given pθ(o,a ), DP’s choice to model the data distribution
through pθ(a|o)also stems from the computational burden of diffusion at test time: generating actions together with
observations would require a large number of denoising steps—an unnecessarily slow and ultimately unhelpful process,
given that robotics focuses on producing controls rather than reconstructing observations.
In practice, conditioning on observation data is achieved conditioning the noise regressorϵθ introduced in eq. 44 on a
stack ofHo observations, resulting in theconditional, simplified diffusion objective:
L(θ) =E t,at:t+Ha,ϵ

∥ϵ−ϵ θ(√¯αtat:t+Ha +ϵ
√
1−¯αt,t,o t−Ho:t)∥2
,(51)
t∼U({1,...,T}), a t:t+Ha,ot−Ho:t∼D, ϵ∼N(0,I).
Note how in eq. 51 the noise regressor is conditioned on both the latent variable rankt andon a stack of previous
observationsot−Ho:t. Chi et al. (2024) claim the combination of (1) conditioning on a horizon of previous observations
and (2) predicting multiple actions into the future allows DP tocommit to specific modesin the data at inference
time, which proves essential for good performance and avoiding undecisiveness.
Figure 31 shows the convolution-based version of the architecture proposed by Chi et al. (2024), illustrating inference
on a single sample drawn fromD, for simplicity. The starting, arbitrarily noisy chunk ofHa actions ˜at:t+Ha is first
mapped to a (learned) high-dimensional space. Similarily, both image observations and poses are also embedded
before being aggregated to the action embeddings. Then, a U-Net (Ronneberger et al., 2015) is trained to regress
the noise added into˜at:t+Ha, conditioned on observation information at every layer, thus seeking to optimize eq. 51.
At inference time, the noise predictor is used to predict the quantity of noise at everyt∈ [T,..., 0]and iteratively
subtract it from˜at:t+Ha, reversing the diffusion process simulated in training conditioned onot−Ho:t to predictat:t+Ha.
DP can be trained with as little as 50-150 demos (ca. 15-60 minutes of teleoperation data), and exhibit strong
performance on a variety of simulated and real-world tasks, including dexterous and deformable manipulation tasks
such as sauce pouring and yoga-mat unrolling. Notably, the authors ablated the relevance of using RGB camera streams
as input to their policy, and observed how high frame-rate visual observations can be used to attain performance
(measured as success rate) comparable to that of state-based policies, which are typically trained in simulation with
priviledged information not directly available in real-world deployments. As high-frame rate RGB inputs naturally
accomodate for dynamic, fast changing environments, Chi et al. (2024)’s conclusion offers significant evidence for
learning streamlined control policies directly from pixels. In their work, Chi et al. (2024) also ablate the performance
of DP against the size of the dataset collected, showing that DP reliably outperforms the considered baseline for
49

[PAGE 50]

all benchmark sizes considered. Further, in order accelerate inference, Chi et al. (2024) employ Denoising Diffusion
Implicit Models (Song et al., 2022), a variant of Denoising Diffusion Probabilistic Models (Ho et al., 2020) (DDPM)
adopting a strictly deterministic denoising paradigm (differently from DDPM’s natively stochastic one) inducing
the same final distribution’s as DDPM’s, and yet resulting in 10x less denoising steps at inference time (Chi et al.,
2024). Across a range of simulated and real-world tasks, Chi et al. (2024) find DPs particularly performant when
modeling ϵθ with a transformer-based network, although the authors note the increased sensitivity of transformer
networks to hyperparameters. Thus, Chi et al. (2024) explicitly recommend starting out with a simpler, convolution-
based architecture for diffusion (Figure 31), which is however reported to be biased towards learning low-frequency
components (Tancik et al., 2020), and thus may prove more challenging to train with non-smooth action sequences.
4.3.1 Code Example: Training and Using Diffusion Policies in Practice
Code 9: Training Diffusion Policy
https://github.com/fracapuano/robot-learning-tutorial/blob/main/snippets/ch4/03_training_diffusion.
py
1from pathlib import Path
2
3import torch
4
5from lerobot . configs . types import F e a t u r e T y p e
6from lerobot . da ta set s . l e r o b o t _ d a t a s e t import LeRobotDataset , L e R o b o t D a t a s e t M e t a d a t a
7from lerobot . da ta set s . utils import d a t a s e t _ t o _ p o l i c y _ f e a t u r e s
8from lerobot . po li cie s . d i f f u s i o n . c o n f i g u r a t i o n _ d i f f u s i o n import D i f f u s i o n C o n f i g
9from lerobot . po li cie s . d i f f u s i o n . m o d e l i n g _ d i f f u s i o n import D i f f u s i o n P o l i c y
10from lerobot . po li cie s . factory import m a k e _ p r e _ p o s t _ p r o c e s s o r s
11
12
13def m a k e _ d e l t a _ t i m e s t a m p s ( d e l t a _ i n d i c e s : list [ int ] | None , fps : int ) -> list [ float ]:
14if d e l t a _ i n d i c e s is None :
15return [0]
16
17return [ i / fps for i in d e l t a _ i n d i c e s ]
18
19
20o u t p u t _ d i r e c t o r y = Path ( " outputs / r o b o t _ l e a r n i n g _ t u t o r i a l / d i f f u s i o n " )
21o u t p u t _ d i r e c t o r y . mkdir ( parents = True , ex is t_o k = True )
22
23# Select your device
24device = torch . device ( " mps " ) # or " cuda " or " cpu "
25
26d a t a s e t _ i d = " lerobot / s v l a _ s o 1 0 1 _ p i c k p l a c e "
27
28# This s p e c i f i e s the inputs the model will be e x p e c t i n g and the outputs it will produce
29d a t a s e t _ m e t a d a t a = L e R o b o t D a t a s e t M e t a d a t a ( d a t a s e t _ i d )
30f ea tu re s = d a t a s e t _ t o _ p o l i c y _ f e a t u r e s ( d a t a s e t _ m e t a d a t a . f ea tu res )
31
32o u t p u t _ f e a t u r e s = { key : ft for key , ft in fe atu re s . items () if ft . type is F e a t u r e T y p e . ACTION }
33i n p u t _ f e a t u r e s = { key : ft for key , ft in f ea tu re s . items () if key not in o u t p u t _ f e a t u r e s }
34
35cfg = D i f f u s i o n C o n f i g ( i n p u t _ f e a t u r e s = input_features , o u t p u t _ f e a t u r e s = o u t p u t _ f e a t u r e s )
36policy = D i f f u s i o n P o l i c y ( cfg )
37preprocessor , p o s t p r o c e s s o r = m a k e _ p r e _ p o s t _ p r o c e s s o r s (
38cfg , d a t a s e t _ s t a t s = d a t a s e t _ m e t a d a t a . stats
39)
40
41policy . train ()
42policy . to ( device )
43
44# To perform action chunking , ACT expects a given number of actions as targets
45d e l t a _ t i m e s t a m p s = {
46" o b s e r v a t i o n . state " : m a k e _ d e l t a _ t i m e s t a m p s (
47cfg . o b s e r v a t i o n _ d e l t a _ i n d i c e s , d a t a s e t _ m e t a d a t a . fps
48) ,
49" action " : m a k e _ d e l t a _ t i m e s t a m p s ( cfg . a c t i o n _ d e l t a _ i n d i c e s , d a t a s e t _ m e t a d a t a . fps ) ,
50

[PAGE 51]

50}
51
52# add image fe atu re s if they are present
53d e l t a _ t i m e s t a m p s |= {
54k : m a k e _ d e l t a _ t i m e s t a m p s ( cfg . o b s e r v a t i o n _ d e l t a _ i n d i c e s , d a t a s e t _ m e t a d a t a . fps )
55for k in cfg . i m a g e _ f e a t u r e s
56}
57
58# I n s t a n t i a t e the dataset
59dataset = L e R o b o t D a t a s e t ( dataset_id , d e l t a _ t i m e s t a m p s = d e l t a _ t i m e s t a m p s )
60
61# Create the o p t i m i z e r and d a t a l o a d e r for offline tr ain in g
62o p t i m i z e r = cfg . g e t _ o p t i m i z e r _ p r e s e t (). build ( policy . p a r a m e t e r s ())
63b a t c h _ s i z e = 32
64d a t a l o a d e r = torch . utils . data . D a t a L o a d e r (
65dataset ,
66b a t c h _ s i z e = batch_size ,
67shuffle = True ,
68p i n _ m e m o r y = device . type != " cpu " ,
69d r o p _ l a s t = True ,
70)
71
72# Number of tr ain in g steps and logging f r e q u e n c y
73t r a i n i n g _ s t e p s = 1
74l og _f re q = 1
75
76# Run t rai ni ng loop
77step = 0
78done = False
79while not done :
80for batch in d a t a l o a d e r :
81batch = p r e p r o c e s s o r ( batch )
82loss , _ = policy . forward ( batch )
83loss . b ac kw ar d ()
84o p t i m i z e r . step ()
85o p t i m i z e r . z e r o _ g r a d ()
86
87if step % lo g_ fr eq == 0:
88print ( f " step : { step } loss : { loss . item ():.3 f } " )
89step += 1
90if step >= t r a i n i n g _ s t e p s :
91done = True
92break
93
94# Save the policy checkpoint , a l o n g s i d e the pre / post p r o c e s s o r s
95policy . s a v e _ p r e t r a i n e d ( o u t p u t _ d i r e c t o r y )
96p r e p r o c e s s o r . s a v e _ p r e t r a i n e d ( o u t p u t _ d i r e c t o r y )
97p o s t p r o c e s s o r . s a v e _ p r e t r a i n e d ( o u t p u t _ d i r e c t o r y )
98
99# Save all assets to the Hub
100policy . p u s h _ t o _ h u b ( " f r a c a p u a n o / r o b o t _ l e a r n i n g _ t u t o r i a l _ d i f f u s i o n _ e x a m p l e _ m o d e l " )
101p r e p r o c e s s o r . p u s h _ t o _ h u b ( " f r a c a p u a n o / r o b o t _ l e a r n i n g _ t u t o r i a l _ d i f f u s i o n _ e x a m p l e _ m o d e l " )
102p o s t p r o c e s s o r . p u s h _ t o _ h u b ( " f r a c a p u a n o / r o b o t _ l e a r n i n g _ t u t o r i a l _ d i f f u s i o n _ e x a m p l e _ m o d e l " )
Code 10: Using Diffusion Policy
https://github.com/fracapuano/robot-learning-tutorial/blob/main/snippets/ch4/04_using_diffusion.py
1import torch
2
3from lerobot . cameras . opencv . c o n f i g u r a t i o n _ o p e n c v import O p e n C V C a m e r a C o n f i g
4from lerobot . da ta set s . l e r o b o t _ d a t a s e t import L e R o b o t D a t a s e t M e t a d a t a
5from lerobot . po li cie s . d i f f u s i o n . m o d e l i n g _ d i f f u s i o n import D i f f u s i o n P o l i c y
6from lerobot . po li cie s . factory import m a k e _ p r e _ p o s t _ p r o c e s s o r s
7from lerobot . po li cie s . utils import b u i l d _ i n f e r e n c e _ f r a m e , m a k e _ r o b o t _ a c t i o n
8from lerobot . robots . s o 1 0 0 _ f o l l o w e r . c o n f i g _ s o 1 0 0 _ f o l l o w e r import S O 1 0 0 F o l l o w e r C o n f i g
9from lerobot . robots . s o 1 0 0 _ f o l l o w e r . s o 1 0 0 _ f o l l o w e r import S O 1 0 0 F o l l o w e r
51

[PAGE 52]

10
11device = torch . device ( " mps " ) # or " cuda " or " cpu "
12m od el _i d = " f r a c a p u a n o / r o b o t _ l e a r n i n g _ t u t o r i a l _ d i f f u s i o n _ e x a m p l e _ m o d e l "
13
14model = D i f f u s i o n P o l i c y . f r o m _ p r e t r a i n e d ( mod el _i d )
15
16d a t a s e t _ i d = " lerobot / s v l a _ s o 1 0 1 _ p i c k p l a c e "
17# This only d o w n l o a d s the m et ad ata for the dataset , ~10 s of MB even for large - scale da ta se ts
18d a t a s e t _ m e t a d a t a = L e R o b o t D a t a s e t M e t a d a t a ( d a t a s e t _ i d )
19preprocess , p o s t p r o c e s s = m a k e _ p r e _ p o s t _ p r o c e s s o r s (
20model . config , model_id , d a t a s e t _ s t a t s = d a t a s e t _ m e t a d a t a . stats
21)
22
23M A X _ E P I S O D E S = 5
24M A X _ S T E P S _ P E R _ E P I S O D E = 20
25
26
27# # find ports using lerobot - find - port
28f o l l o w e r _ p o r t = ... # s o m e t h i n g like "/ dev / tty . u s b m o d e m 5 8 7 6 0 4 3 1 6 3 1 "
29
30# # the robot ids are used the load the right c a l i b r a t i o n files
31f o l l o w e r _ i d = ... # s o m e t h i n g like " f o l l o w e r _ s o 1 0 0 "
32
33# Robot and e n v i r o n m e n t c o n f i g u r a t i o n
34# Camera keys must match the name and r e s o l u t i o n s of the ones used for t ra in in g !
35# You can check the camera keys e xpe ct ed by a model in the info . json card on the Hub
36c a m e r a _ c o n f i g = {
37" side " : O p e n C V C a m e r a C o n f i g ( i n d e x _ o r _ p a t h =1 , width =640 , height =480 , fps =30) ,
38" up " : O p e n C V C a m e r a C o n f i g ( i n d e x _ o r _ p a t h =1 , width =640 , height =480 , fps =30) ,
39}
40
41r o b o t _ c f g = S O 1 0 0 F o l l o w e r C o n f i g ( port = follower_port , id = follower_id , cameras = c a m e r a _ c o n f i g )
42robot = S O 1 0 0 F o l l o w e r ( r o b o t _ c f g )
43robot . connect ()
44
45
46for _ in range ( M A X _ E P I S O D E S ):
47for _ in range ( M A X _ S T E P S _ P E R _ E P I S O D E ):
48obs = robot . g e t _ o b s e r v a t i o n ()
49o b s _ f r a m e = b u i l d _ i n f e r e n c e _ f r a m e ( obs , d a t a s e t _ m e t a d a t a . features , device )
50
51obs = p r e p r o c e s s ( o b s _ f r a m e )
52
53action = model . s e l e c t _ a c t i o n ( obs )
54action = p o s t p r o c e s s ( action )
55action = m a k e _ r o b o t _ a c t i o n ( action , d a t a s e t _ m e t a d a t a . f ea tu re s )
56robot . s e n d _ a c t i o n ( action )
57
58print ( " Episode fi nis he d ! S ta rti ng new episode ... " )
4.4 Optimized Inference
Modern visuomotor policies outputaction chunks–sequencesπ(ot) =
 
at,at+1,...,a t+Ha

=A t withA t a sequence
of Ha≫ 1low-level commands scheduled for execution in an action queue, all originating from a single environment
observation,ot. Predicting series of actions instead of single commands proved essential in learning complex, multi-
modal behavior (Zhao et al., 2023; Chi et al., 2024), and it also holds the premise to be useful to optimize how
inference is carried out in practice.
A robot may indeed execute an entire action chunkAt beforea new observationot+Ha is passed to the policyπ to
predict the next chunk, which would result in open-loop control between observations captured everyHa timesteps.
Zhao et al. (2023) adopt a different strategy, whereby the robot controller interleaves chunk predictionAt←π (ot)
and chunk consumptionat←PopFront(A t), and computes a new chunk of actions at every timestept, to then
aggregate the predicted chunks on overlapping sections. While adaptive—every observation at every timestepot is
processed—such an approach relies on running inference continuously, which can be prohibitive in resource-constrained
scenarios, such as edge deployments. A less resource-intensive approach is to entirely exhaust the chunkAbefore
predicting a new chunk of actions, a strategy we refer to assynchronous(sync) inference. Sync inference allocates
52

[PAGE 53]

Figure 32 | Asynchronous inference. Illustration of the asynchronous inference stack. Note that the policy can be run on a
remote server, possibly with GPUs.
computation everyHa timesteps, resulting in a reduced computational burden (on average) at control time. In
contrast, sync inference also inherently hinders the responsiveness of robot systems, introducing blind lags due to the
robot beingidlewhile computingA.
One can use the fact that policies output multiple actions at the same time to directly (1) the lack of adaptiveness and
(2) the presence of lags at runtime by decoupling action chunkpredictionAfrom actionexecutionat←PopFront (At).
This decoupled stack, which we refer to asasynchronous(async) inference (1), also enables optimized inference by
allowing action-chunk inference to run on a separate machine, typically equipped with better computational resources
than the ones onboard a robot. In async inference, aRobotClient sends an observationot to a PolicySer ver,
receiving an action chunkAt once inference is complete (Figure 32). In this, we avoid execution lags by triggering
chunk prediction while the control loop is still consuming a previously available chunk, aggregating the previous
and incoming chunks whenever the latter is available to theRobotClient. In turn, async-inference tightens the
loop between action prediction and action execution efficienty, by increasing the frequency at which observations are
processed for chunk prediction while not running inference at every timestep. Crucially, decoupling action prediction
from action execution also allows to allocate more computational resources on a remote policy server sending actions
to the robot client over the network.
Algorithm 1Asynchronous inference control-loop
1:Input:horizonT, chunk sizeH a, thresholdg∈[0,1]
2:Init:captureo 0; sendo 0 toPolicySer ver; receiveA 0←π(o 0)
3:forttoH a do
4:a t←PopFront(At)
5:Execute(a t)▷execute action at stept
6:if |At|
Ha
<gthen▷queue below threshold
7:capture new observation,o t+1
8:ifNeedsProcessing(o t+1)then▷similarity filter, or triggers direct processing
9:async_handle←AsyncInfer(o t+1)▷Trigger new chunk prediction (non blocking)
10: ˜At+1←π(o t+1)▷New queue is predicted with the policy
11:A t+1←f(A t, ˜At+1)▷aggregate overlaps (if any)
12:end if
13:end if
14:ifNotCompleted(async_handle)then
15:A t+1←A t ▷No update on queue (inference is not over just yet)
16:end if
17:end for
53

[PAGE 54]

Figure 33 | Action queue size evolution at runtime for various levels ofg when (A) not filtering out observation based on
joint-space similarity and (B) filtering out near-duplicates observation, measuring their similarity in joint-space.
In practice,asyncinference (1) tightens the control loop by capturing observations more often, eliminating idle gaps
at runtime (2) and directly allows to run inference on more powerful computational resources than the ones typically
available onboard autonomous robotic platforms. Algorithmically, one can attain (1) on theRobotClient-side
by consuming actions from a readily available queue until a given condition on the number of remaining actions
in the queue (|At|/Ha < g) is met. When this condition is triggered, a new observation of the environment is
captured and sent to the (possibly remote)PolicySer ver. To avoid redundant server calls and erratic behavior at
runtime observations are compared in joint-space, and near-duplicates are dropped. Two observations are considered
near-duplicates if their distance in joint-space falls under a predetermined threshold,dlim∈R +. Importantly, should
the queue available to the robot client eventually empty out, the most recent observation is processed regardless of
similarity.
Interestingly, the behavior of async inference can be studied analytically. First, letℓ be a random variable modeling the
time needed to receive an action chunkAafter sending an observationo, i.e. the sum of (1) the time to send across the
observationo between theRobotClientandPolicySer ver, tC→S (2) the inference latency on thePolicySer ver,
ℓS and (3) the time to sendAbetween thePolicySer verandRobotClient, tS→C. Under the (reasonable)
assumption of independence, E[ℓ] = E[tC→S ] + E[ℓS] + E[tS→C ], which can be further simplified toE[ℓ]≃E [ℓS],
assuming communication time is (1) equal in both directions and (2) negligible with respect to the inference latency.
Second, let∆ t be the environment’s control cycle. With a real-world frame-rate of 30 frames-per-second (fps),
∆t = 33ms. Consequently, exhausted queues at runtime—i.e. being idle awaiting for a new chunk—are avoided for
g≥ E[ℓS]/∆t
Ha
. In this, the action queue thresholdg below which to capture and send a new observation for processing
plays a major role relatively to the availability of actions to theRobotClient.
Figure 33 illustrates how the size of the action chunk|At| evolves over time for three representative values ofg,
detailing the following key scenarios:
• Sequential limit( g = 0).The client drains the entire chunk before forwarding a new observation to the server.
During the round-trip latency needed to compute the next chunk, the queue is empty, leaving the robotincapable
of acting. This reproduces the behavior of a fully sequential deployment and results in an average ofE[ℓS]idle
seconds.
• Asynchronous inference(g∈ (0, 1)).Allowing the client to consume a1−g fraction of its available queueAt−1
beforetriggering inference for a new action queueAt, computation is amortized while keeping the queue from
emptying. The overlap between successive chunks provides a buffer against modeling errors without the full cost of
the g = 1regime. The updated queueA t is obtained aggregating queues on the overlapping timesteps between
At−1 and the incoming ˜At.
• Sync-inference limit(g = 1).As an extreme case, and in keeping with Zhao et al. (2023), an observation is sent
ateverytimestep. The queue is therefore almost always filled, with only a minor saw-tooth due to∆t/E[ℓs]< 1.
While maximally reactive, this setting incurs one forward pass per control tick and can prove prohibitively expensive
on limited hardware. Importantly, because the client is consuming actions while the server computes the next
chunk, the available queue never gets entirely filled.
Figure 33 emphasizes the trade-off governed byg: small values ofg result in idle periods, whereasg≈ 1assumes a
54

[PAGE 55]

highly accurate model and pays a significant compute price. In practice, choosingg∈ (0, 1)allows to strike a balance
between reactivity against resource budgets. If not for the aforementioned similarity filter, theRobotClient would
send observations for processing every(1−g)Ha·∆tseconds, receiving a new chunk of actions every(1−g)Ha·∆t+E[ℓS],
on average. The presence of the filter for observation similarity dilates this processing time, and serves the scope
of avoiding the robot stalling due to the queue being constantly integrated with an incoming, nearly identical,
action chunk. In particular, Figure 33 results in a queue which is filled with incoming actionsunlessnear-duplicate
observations are filtered out from the processing pipeline. For clarity, the red arrow in 33 highlights a timestep where
the observation similarity mechanism is bypassed, forcing a (nearly identical) observation to be processed as the queue
results empty.
4.4.1 Code Example: Using Async Inference
Code 11: Spinning up a Remote Server
https://github.com/fracapuano/robot-learning-tutorial/blob/main/snippets/ch4/05_policy_server.py
1from lerobot . a s y n c _ i n f e r e n c e . configs import P o l i c y S e r v e r C o n f i g
2from lerobot . a s y n c _ i n f e r e n c e . p o l i c y _ s e r v e r import serve
3
4host = ... # s o m e t h i n g like " 1 2 7 . 0 . 0 . 1 " if you're e xpo si ng to l o c a l h o s t
5port = ... # s o m e t h i n g like 8080
6
7config = P o l i c y S e r v e r C o n f i g (
8host = host ,
9port = port ,
10)
11serve ( config )
Code 12: Attaching a Robot Client
https://github.com/fracapuano/robot-learning-tutorial/blob/main/snippets/ch4/06_robot_client.py
1import t h r e a d i n g
2from lerobot . robots . s o 1 0 0 _ f o l l o w e r import S O 1 0 0 F o l l o w e r C o n f i g
3from lerobot . cameras . opencv . c o n f i g u r a t i o n _ o p e n c v import O p e n C V C a m e r a C o n f i g
4from lerobot . a s y n c _ i n f e r e n c e . configs import R o b o t C l i e n t C o n f i g
5from lerobot . a s y n c _ i n f e r e n c e . r o b o t _ c l i e n t import R o b o t C l i e n t
6from lerobot . a s y n c _ i n f e r e n c e . helpers import v i s u a l i z e _ a c t i o n _ q u e u e _ s i z e
7
8# these cameras must match the ones e xpe ct ed by the policy ( use lerobot - find - cameras )
9# check the config . json on the Hub for the policy you are using to see the ex pec te d camera specs
10c a m e r a _ c f g = {
11" top " : O p e n C V C a m e r a C o n f i g ( i n d e x _ o r _ p a t h =0 , width =640 , height =480 , fps =30) ,
12" side " : O p e n C V C a m e r a C o n f i g ( i n d e x _ o r _ p a t h =1 , width =640 , height =480 , fps =30)
13}
14
15# # find ports using lerobot - find - port
16f o l l o w e r _ p o r t = ... # s o m e t h i n g like "/ dev / tty . u s b m o d e m 5 8 7 6 0 4 3 1 6 3 1 "
17
18# # the robot ids are used the load the right c a l i b r a t i o n files
19f o l l o w e r _ i d = ... # s o m e t h i n g like " f o l l o w e r _ s o 1 0 0 "
20
21r o b o t _ c f g = S O 1 0 0 F o l l o w e r C o n f i g (
22port = follower_port ,
23id = follower_id ,
24cameras = c a m e r a _ c f g
25)
26
27s e r v e r _ a d d r e s s = ... # s o m e t h i n g like 1 2 7 . 0 . 0 . 1 : 8 0 8 0 if using l o c a l h o s t
28
29# 3. Create client c o n f i g u r a t i o n
30c l i e n t _ c f g = R o b o t C l i e n t C o n f i g (
31robot = robot_cfg ,
55

[PAGE 56]

32s e r v e r _ a d d r e s s = server_address ,
33p o l i c y _ d e v i c e = " mps " ,
34p o l i c y _ t y p e = " smolvla " ,
35p r e t r a i n e d _ n a m e _ o r _ p a t h = " f r a c a p u a n o / s m o l v l a _ a s y n c " ,
36c h u n k _ s i z e _ t h r e s h o l d =0.5 , # g
37a c t i o n s _ p e r _ c h u n k =50 , # make sure this is less than the max actions of the policy
38)
39
40# 4. Create and start client
41client = R o b o t C l i e n t ( c l i e n t _ c f g )
42
43# 5. Provide a textual d e s c r i p t i o n of the task
44task = ...
45
46if client . start ():
47# Start action re ce iv er thread
48a c t i o n _ r e c e i v e r _ t h r e a d = t h r e a d i n g . Thread ( target = client . receive_actions , daemon = True )
49a c t i o n _ r e c e i v e r _ t h r e a d . start ()
50
51try :
52# Run the control loop
53client . c o n t r o l _ l o o p ( task )
54except K e y b o a r d I n t e r r u p t :
55client . stop ()
56a c t i o n _ r e c e i v e r _ t h r e a d . join ()
57# ( O p t i o n a l l y ) plot the action queue size
58v i s u a l i z e _ a c t i o n _ q u e u e _ s i z e ( client . a c t i o n _ q u e u e _ s i z e )
56

[PAGE 57]

Figure 34 | Fields within ML such as Computer Vision and NLP converged on the development of foundation models, trained
on a variety of large scale models and capable to perform multiple downstream tasks (top). Conversely, robotics suffered from
limited standardization in terms of the architectures used, and siloed, task specific datasets, incurring in a high degree of
fragmentation which traditionally hindered the development of generalist models for robotics in favour of task-specific models
(bottom).
5 Generalist Robot Policies
Specialization is for insects
Robert A. Heinlein
TL;DR
Openly available, large-scale datasets and the development of stable-to-train, expressive and efficient architectures
fostered research on the development of generalist robot policies that can operate across embodiment and tasks.
The advent of large models trained on internet-scale datasets has drastically influenced fields like Computer Vision
(CV) and Natural Language Processing (NLP), shifting the previously task-specific paradigm towards combining (1) an
initial, task-agnostic large-scale pre-training stage and a (2) task-specific, adjustment phase. Thispre-train-and-adaptat
paradigm has now largely replaced more classic approaches consisting of task-specific data collection, curation and
model training in many subdomains within CV and NLP, and it is motivated by the main drawback of limited
scalability fortask-specific approaches, which have been traditionally more labor intensive. Factors including (1)
the advancements in generalist models learned with self-supervision for perception (Oquab et al., 2024) or semantic
understanding (Devlin et al., 2019) and (2) the popularization of collective efforts to aggregate large-scale openly
available datasets (O’Neill et al., 2025; Khazatsky et al., 2025) are increasingly pushing the field of robot learning
towards the pre-train-and-adapt paradigm. This shift taps into the long-standing challenge of developing generalist
robot policies, and holds the premise to surpass traditionally siloed approaches to robotics problems and develop
afoundation robotics model. While Section 4 introduced methods for learningsingle-task policiessuch as ACT
or Diffusion Policy, in this section we present advancements in developinggeneralist, multi-task, policies, capable
of performing a wide range of tasks across different environments and embodiments, and guided by unstructured
instructions typically given in plain, natural language.
57

[PAGE 58]

Figure 35 | Early efforts in the development of generalist models for robotics include BC-Zero (Jang et al., 2022), RT-1 (Brohan
et al., 2023b), and RT-2 (Brohan et al., 2023a): large scale models trained on thousands of demonstrations. The open release
of the Open-X (O’Neill et al., 2025) and DROID datasets (Khazatsky et al., 2025) fostered the development of open source
models: OpenVLA (Kim et al., 2024),π0 (Black et al., 2024) and SmolVLA (Shukor et al., 2025).
5.1 Preliminaries: Models and Data
The remarkable success of foundation models in NLP and CV seems to be increasingly predicated on two core
principles: architectural innovation and (joint) data-compute scaling. Indeed, the transformer architecture proved very
effective in capturing long-range dependencies in a variety of data formats, and its stability and expressivity made it
thede factostandard for modern large-scale models trained on internet-scale datasets. However, in stark contrast with
large-scale NLP and CV datasets (Raffel et al., 2023; Deng et al., 2009), robotics has historically developed around
small, task-specific datasets. In turn, this traditionally hindered scalability across problems as well as results, posing
concrete challenges to developing general-purpose robot learning algorithms. Indeed, differently from the wealth
of relatively readily-available task-agnostic text and images datasets on the internet, robotics data isintrinsically
embodiedand thus task-specific: datasets collected formanipulationdiffer significantly fromlocomotion. In particular,
since each expert trajectory is tied to a specific robot platform and the operating conditions of its environment
and task, data heterogeneity has long posed amethodologicalchallenge for scaling robotics datasets via aggregation.
Further, datasets consisting of expert demonstrations are (1) intrinsically more expensive to collect and (2) notoriously
heterogeneous—different human experts may perform the same task in very different. Beyond this, heterogeneity also
raisesconceptualissues: naively mixing data across embodiments can induce negative transfer, as control strategies
developed in isolation for different robot systems in different environments may even conflict when combined. Thus,
the high degree of fragmentation of robotics datasets and tasks has traditionally led to the development ofspecialist
policies, trained on small, task-specific datasets, developed to perform well at their designated task but that fail to
generalize to new deployment scenarios (Figure 34).
Driven by the goal of developing generalist robot policies, the research community has increasingly explored how
insights and techniques from other areas of ML can be integrated into robotics. Figure 35 shows a timeline of some
of the most popular contributions attempting at developing generalist policies. Starting from BC-Zero, a latent
variable model trained on 25k+ demonstrations, the field has now evolved intoπ0, a transformer-based model trained
on 10M+ demonstrations and exhibiting strong few-shot capabilities across tasks and embodiments. In between,
Robotics Transformer 1 (RT-1) (Brohan et al., 2023b) represented a significant step in the direction of developing a
generalist robot policies over prior work including (1) BC-Zero (Jang et al., 2022) and (2) Gato (Reed et al., 2022), in
that Brohan et al. (2023b) use a much larger and diverse set of training tasks compared to both BC-Zero and Gato.
In particular, RT-1 uses a transformer architecture, and is trained on as many as 130k human-recorded trajectories
collected over 13 robots and over 17 months. RT-1 learns to process a history of camera images and a natural language
instruction, and feeds the resulting sequence of high-dimensional tokens to a transformer, trained using aclassification
loss on a discretized actions spaceconsisting of six different 256-bins, one for each joint of a 6-dof robotic arm.
In a follow-up work, the same group of authors propose a modified method to learn generalist models, leveraging (1)
a more powerful architecture and (2) scaling up the dataset used (Brohan et al., 2023a, RT-2). In RT-2, Brohan et al.
(2023a) propose inheriting internet-scale semantic knowledge from large-scale multi-modal datasets to learn a single,
unified modelfor robotics control. Such a model, termedVision-Language-Action(VLA) in the original RT-2 paper,
effectively casts robot control as a language-modeling problem, and in particular as a Visual Question-Answering
(VQ&A) task, in which the output token space used to representtextual tokensis shared with the8-bits tokensused
58

[PAGE 59]

Figure 36 | Robot learning is undergoing a paradigmatic shift: centralized data collections (A, left) are increasingly larger,
often comprising millions of demonstrations, while (A, right) decentralized data collection efforts are becoming an alternative for
large scale data collection. (B) Generalist models are also becoming increasingly smaller and easier to run on limited hardware.
to represent the 256 (28) actuation levels of a 6-dof robot. In their work, Brohan et al. (2023a) propose co-fine-tuning
large-scale VLMs such as PaLIX (Chen et al., 2023) or PaLM-E (Driess et al., 2023) on a mix of (1) web and (2)
robotics data, complementing VQ&A training with robotics-specific signal, and learning to directly output robot
actions in a shared token space for visual and language inputs. In their work, the authors claim using large models
trained on internet-scale data as backbones for VLAs allows models to tap into the rich semantic knowledge embedded
in the VLM’s parameters, interpreting instructions and unseen objects by connecting them to concepts acquired while
pre-training. For instance, Brohan et al. (2023a) show that while RT-2 has never been explicitly trained to repurpose
tools for ahammeringtask, it can still combine its semantic understanding of images, so that when asked which
object between (1) a piece of paper, (2) a pair of headphones or (3) a rock may be used instead of a hammer, it
correctly answers (3).
Traditionally, research efforts revolved around not only training models, but also proposing datasets for the community,
a costly and time-consuming process. Due to the aforementioned embodiment gap, the data used in research efforts in
robot learning have traditionally proved rather fragmented, tailored to the specific task considered by the specific group
of researchers who collected it, which ultimately hindered integration. The Open X-Embodiment project (O’Neill et al.,
2025) was a landmark collaboration effort to address data fragmentation, by curating the aggregation of 60existing
robotics datasets from 22 different robot embodiments and 21 institutions across the world, and resulted in a total 1.4M
of cross-embodiments, cross-tasks, openly-available trajectories. Besides the contribution of an aggregate, large scale
dataset, O’Neill et al. (2025) also demonstrated significant positive transferacross tasks and embodiments, showing
that a single model trained on multi-embodiment data can outperform specialist models trained on their respective
single-embodiment datasets. The Distributed Robot Interaction Dataset (DROID) (Khazatsky et al., 2025) represents
another significant step towards addressing the problem of scarse and disaggregated data in robot learning, providing
a unique dataset consisting of 75k+ human demonstrations collected in realistic (in-the-wild) manipulation settings,
providing another cornerstone for building general-purpose robot policies. Recently, foundational datasets curated
through large, centralized efforts, are increasingly complemented by decentralized, community-driven contributions of
robotics data. Software libraries likelerobot have been instrumental in enabling decentralized collection of large
amounts of data, providing the infrastructure for researchers and practitioners to easily contribute trajectories from a
wide range of embodiments, democratizing data access via distributed collection.
Despite these advancements, the success of large, proprietary models like RT-1 and RT-2, highlighted a growing
accessibility gap in robotics research, as training and deploying large-scale robotics foundation models requires
computational resources simply unattainable for most research institutions. The OpenVLA project (Kim et al.,
2024) emerged in direct contrast to traditionally closed-source efforts to develop VLAs. In particular, Kim et al.
(2024) trained OpenVLA by exclusively leveraging openly available data (970k+ trajectories from the Open-X
dataset), and openly shared their training recipes alongside the model weights. Architecturally, OpenVLA integrates
a pre-trained vision encoder to project visual tokens into the embedding space of the Llama2-7B (Touvron et al.,
2023) language-model backbone. The language model backbone is then used to predictdiscrete action tokensover
256 activation levels.
Figure 36 shows the current trends in robot learning in terms of size and nature of the robotics datasets contributed,
together with the size and accessibility of the available models. As datasets collected via centralized, cross-institutions
cooperation of increasing size are made available for the research community, decentralized datasets collected by
individual researchers and practitioners also gained traction, closing the gap with academic benchmarks thanks to
59

[PAGE 60]

community-contributed datasets. Further, models used across tasks and embodiments are increasingly becoming much
more compute-efficient, and as a result the models’ size has been consistently reducing over time, with consequent
gains for autonomous robots in real-world, resource-constrained environments.
5.2 VLAs
Modern recipes to train large scale VLAs extend early efforts to learn foundation models from large amounts of data via
BC, introducing significant advancements concerning both architectural and procedural aspects. From an architectural
perspective, modern VLAs such asπ0 (Black et al., 2024) leverage aunified transformer modelfor efficiency of
computation, while maintaining specialized sub-components within the model for visual perception and action
prediction, enabling cross-task performance via language conditioning. Crucially, modern VLAs includingπ0 (Black
et al., 2024) and SmolVLA (Shukor et al., 2025) adoptunifiedtransformer models employing disjoint set of weights
(experts) for both compute-efficient visual-semantic understanding as well as control. Procedurally, VLAs complement
advanced Vision-Language Model (VLM) backbones with action-specific modules (1) adopting mid-sizedaction experts
to model continuous actions distributionsp(at:t+Ha|ot)—avoiding discrete action tokens entirely—and (2) relying
onaction chunking(Zhao et al., 2023, Section 4) as a strategy to reduce error compounding when predicting multiple
actions learning from inherently non-i.i.d. data, such as demonstration data.
These architectural and procedural innovations present three benefits over task-specific methods. First, developing
architectures that exploit internet-scale pre-trained backbones allows to fully capitalize on the vast world knowledge
and skills state-of-the-art VLMs exhibit, preventig models from needing to learn visual, linguistic and semantic
concepts from scratch. Second, using generative models for continuous action distributions allows to learn rich,
multimodal data distributions, a much more likely scenario in the big-data regime which is typically tackled while
developing generalist policies. Further, introducing separate components for perception and action planning enable
using Mixture of Experts (MoE) architectures (Fedus et al., 2022), which are often more efficient to run—a key
feature for models deployed in real-world scenarios. This new paradigm has been at the core of some of the most
capable generalist policies developed to date, capable to few-shot adapt to novel tasks and to perform highly dexterous
manipulation tasks ranging from end-to-end folding laundry to bussing tables (Black et al., 2024).
5.2.1 VLMs for VLAs
VLMs are designed to handle both visual and textual modalities, most commonly by taking both images and text as
inputs, generating text conditioned on the visual context. Recent advances in VLMs have been driven by the success
of LLMs, with many approaches building upon pretrained LLMs and adopting similar training paradigms to the
ones used in language modeling. Typically, VLMs (Alayrac et al., 2022; Laurençon et al., 2024; Lin et al., 2024) are
constructed by integrating a pretrained vision encoder (Radford et al., 2021; Zhai et al., 2023; Fini et al., 2024) with
a pretrained LLM (Grattafiori et al., 2024; Jiang et al., 2023). Training then proceeds in multiple multimodal stages,
beginning with a large-scale pretraining on datasets containing image-text pairs (Schuhmann et al., 2022; Byeon et al.,
2022) and interleaved vision-language corpora (Laurençon et al., 2023; Zhu et al., 2023), all followed by a supervised
fine-tuning stage on instruction-tuning datasets (Liu et al., 2023; Tong et al., 2024; Laurençon et al., 2024). The
inherent multimodal nature of VLMs enables them to jointly reason over vision and language. Pre-training on vast
internet-scale datasets allows these models to associate visual patterns with textual descriptions, thereby acquiring a
rich semantic understanding of the world—knowledge about objects, their properties, and relationships—without
explicit supervision for each concept. In turn, integrating VLMs as the perceptual backbone for VLAs allows the
latter to inherit rich, contextual world knowledge from the VLM, sidestepping the need to re-learn visual and semantic
representations. In principle, this also allows the robot to ground high-level natural language instructions in its visual
context, and possibly recognize objects by connecting them to the pre-trained concepts absorbed during pre-training,
improving on the possibility to generalize to novel scenarios.
Recently, compute efficiency has also become a central focus in multi-modal research. Several works aim to reduce
training costs by using smaller, more diverse datasets (Liu et al., 2023; Dai et al., 2023; Bai et al., 2025; Zhu et al.,
2024; Tong et al., 2024), training smaller-scale models (Marafioti et al., 2025; Korrapati, 2024; Yao et al., 2024), or by
adapting pretrained unimodal models by tuning only a small subset of parameters (Shukor et al., 2023; Vallaeys et al.,
2024; Mañas et al., 2023; Koh et al., 2023; Tsimpoukelli et al., 2021; Li et al., 2023). While the majority of VLM
research focuses on image and text modalities, recent work has also demonstrated that similar techniques can be
extended to integrate additional modalities, such as video and audio (Wang et al., 2025; Liu et al., 2024; Zhang et al.,
2025; Kong et al., 2024)—a particularly promising direction of research for robotics applications, where multiple
sensor modalities can be integrated effectively. This trend towards efficiency is paramount for robotics applications,
where policies must operate under the stringent constraints of real-world deployment.
60

[PAGE 61]

Figure 37 | The π0 architecture, as in Black et al. (2024). Vision and language tokens are routed to a VLM backbone which
is prevented from attending robot proprioperceptive states and action tokens, which are instead routed to a smaller subset
of weights within the architecture referred to as "action expert". The architecture is trained with Flow Matching on 10M+
trajectories from a mixture of closed and openly available datasets.
5.3π 0
π0 (Black et al., 2024) introduce a VLA consisting of a MoE architecture consisting of (1) a pre-trained VLM backbone
(Gemma 2.6B (Team et al., 2024)) and (2) a dedicated action expert used to generate continuous actions via flow
matching. Images and language are embedded with PaliGemma, a VLM merging independently encoded visual and
textual features deep in the network (late-fusion), while proprioceptive state and actions chunks are routed to a
smalleraction expert, initialized from scratch. The two separate experts communicate via self-attention layers, but
maintain disjoint weights to obtain query, key and values matrices at each layer, maintaining specialization while
efficiently allocating computation.
Concretely,π0 is a single, unified transformer with two disjoint sets of weightsϕ,θ. A larger VLM backbonefϕ
initialized from Gemma 2.6B processes multiple image frames obtained from multiple cameras points[{It}n
t=1], as
well as a language instruction[ℓt]used to describe the task considered. Concurrently, a 300M-parameteraction expert
based on a similar transformer architecture is used to process both the robot proprioperceptive stateqt and an action
chunkat:t+Ha (Figure 37). The different expert networks operate separately in processing the respective inputs and
turn them into query, key and value matrices, and only share information between each other via self-attention layers.
The outputs from the VLM backbone are disregarded, while the vector field regressed by the action expert is used to
iteratively refine the action process. In particular,π0 uses ablockwise causal attention maskover tokens belonging to
three separate blocks: (1) image and language tokensTi obtained from[{It}n
t=1,ℓt], (2) proprioperceptive tokensTq
obtained fromqt, and (3) the action tokensTa for items in the chunkaτ
t:t+Ha at timeτ in the flow-matching process.
Notably,withineach block the attention operations are bidirectional, whileacrossblocks, future blocks are masked
out. Formally, this corresponds to using an attention mask like:
A=


Ti Tq Ta
Ti 1 0 0
Tq 1 1 0
Ta 1 1 1

,1:Bidirectional Attention,0:Masked Attention
Note howintra-block directional attention allows tokens to communicate freely, whileinter-block communication is
mediated by the attention maskA.Blockwise causal maskingeffectively prevents the pre-trained perception-language
tokens from attending to robotics-tokens, likely out of distribution for VLM backbones traditionally trained on large
corpora of internet, non-robotics, data. Crucially, because communication is obstructed between image-language
tokens, proprioperceptive tokens and action tokens, one can cache keys and values across denoising steps at runtime
time, incuring in a reduced computational footprint and faster inference.
61

[PAGE 62]

Inπ0, both the VLM backbone and action expert are update using aflow matchingloss, and in particular are updated
minimizing:
L(ϕ,θ) =E τ,ϵ,ot,at:t+Ha
hvθ(τat:t+Ha + (1−τ)ϵ| {z }
˜at:t+Ha
, ot, τ)−(ϵ−a t:t+Ha)
2i
,(52)
τ∼Beta [0,s](1.5,1), ϵ∼N(0,I), o t,at:t+Ha∼D
where the two experts parametrized by the separate weightsϕ,θ interact with each other via self-attention layers only, so
that the action expertvθ internal computations also depend on the VLM backbone’s parametersϕ. Importantly, Black
et al. (2024) minimize eq. 52 over both the multimodal backbone and action expert parameters, thus updating both
the internal representations of the VLM and action-expert weights using BC-specific gradients. In contrast, Driess
et al. (2025) later show that failing to insulate the VLM knowledge from the flow matching gradients actually harms
performance.
At runtime, inference is performed iteratively refining action chunks while numerically forward-integrating the vector
field predicted by the action expert,
aτ+δ
t:t+Ha =a τ
t:t+Ha +δvθ(aτ
t:t+Ha,ot)(53)
Flow matching (Lipman et al., 2023, Section4.1.3) can be seen as a continuous time, deterministic generalization
of diffusion processes, and has proven effective in modeling highly complex multi-modal distributions, including
those over images and video. In turn, the application of flow matching to large-scale datasets of multiple human
behaviors across tasks and embodiments appears rather consequential, particularly considering how it can enable
faster inference via a limited number of denoising steps at test time—as few as 10, inπ0. In particular, the action
expert is implemented as a conditional flow matching model. Each action token embeds a noisy actionaτ
i∈a τ
t:t+Ha,
alongside a sinusoidal encoding of theflow processtimestepτ. The action expert then leverages full bidirectional
attention across theHa action tokens provided, and also attends to previous proprioperceptive and image-language
tokens. Interestingly, differently from a standard flow matching pipeline (Lipman et al., 2023),τ isnotsampled from
a uniform distributionτ∼U ([0, 1]), but rather obtained fromτ∼Beta (1.5, 1)defined on the[0 ,s ],s< 1support
(Figure 38).
Figure 38 | Unlike more traditional flow-matching
algorithms, π0 uses a modified distribution to sam-
ple the timestepτ from during training and infer-
ence, favouring earlier timestamps corresponding
to noisier chunks.
Using such Beta distribution emphasizes higher noise levels dur-
ing training, a choice Black et al. (2024) argue allowsπ0 to fo-
cus on learning to reconstruct the mean of the data distribution
E[at:t+Ha|ot]over an identity map during training, in keeping
with Esser et al. (2024). To further optimize performance and
reduce inference time, Black et al. (2024) propose reducing the
support of the timestep distribution to[0,s ], s <1, as for any
forward-integration step sizeδ = 1−s timesteps aboves are never
sampled at inference time.
Besides adopting a MoE architecture with a VLM backbone initial-
ized from a pre-trained model and trained jointly with an action
expert via flow matching,π0 also relies on a unique pre-training
corpus comprising of a mix of proprietary and open data totaling
10M+ trajectories, which in their work Black et al. (2024) claim
to be the largest dataset used to develop a foundational robotics
model to date. The dataset used to trainπ0—referred to as "the
π dataset"—comprises a private, undisclosed portion obtained via
expert teleoperation as well as openly available datasets including
Open-X and DROID, with only≈ 9.1%of the π being openly
available. In theπ dataset, open datasets such as DROID and Open-X are complemeneted with expert trajectories
consisting of dexterous demonstrations tasks spanning 7 robot configurations and 68 different tasks. Crucially, Black
et al. (2024) show that pre-training on theπ dataset yields a broadly capable base model, which can be adapted
via fine-tuning on narrower, higher-quality task data, which induces a fluent multi-stage behavior while retaining
robustness. In particular, Black et al. (2024) report that, across a variety of benchmarks, the version ofπ0 pretrained
on theπ dataset and fine-tuned on extra high-quality data demonstrationsconsistently outperformsaπscratch
0 baseline
trained entirely from scratch for a given specific task, which further underscores the relevance of pretraining on theπ
dataset. Black et al. (2024) do also offer an intuition behind this finding: high-quality demonstrations of a given task
62

[PAGE 63]

tend to omit failure data, which inherently prevents an autonomous agent to learn how to recover from near-failure
states. In turn, robot trained on high-quality data exclusively with BC may as well be entirely incapable to recover
from failure. Conversely, large scale collections of human demonstrations are typically much more diverse (if anything,
for their sheer scale), and typically contain rich and diverse information, which may prove suboptimal for any given
task when considered in isolation but which proves invaluable in coupling with a small, narrower set of demonstrations.
Lastly, Black et al. (2024) present cross-embodiment experiments where they demonstrateπ0’s ability to control
both mobile and static manipulator robots with varying arm embodiments. The emergence of cross-embodiment
capabilities is largely to be attributed to the presence of large scale cross-embodiment data inπ data mixture, which
is in practice handled byπ0 outputting actions with maximal configuration size across the wholeπ dataset, and
zero-padding robots with fewer dofs.π0 does also rely on exactly three camera views at both training and test time,
and uses masked image slots for training and deployment scenarios with fewer cameras.
5.3.1 Code Example: Usingπ 0
Code 13: Usingπ 0
https://github.com/fracapuano/robot-learning-tutorial/blob/main/snippets/ch5/01_using_pi0.py
1import torch
2
3from lerobot . cameras . opencv . c o n f i g u r a t i o n _ o p e n c v import O p e n C V C a m e r a C o n f i g
4from lerobot . da ta set s . utils import h w _ t o _ d a t a s e t _ f e a t u r e s
5from lerobot . po li cie s . factory import m a k e _ p r e _ p o s t _ p r o c e s s o r s
6from lerobot . po li cie s . pi0 . m o d e l i n g _ p i 0 import P I 0 P o l i c y
7from lerobot . po li cie s . utils import b u i l d _ i n f e r e n c e _ f r a m e , m a k e _ r o b o t _ a c t i o n
8from lerobot . robots . s o 1 0 0 _ f o l l o w e r . c o n f i g _ s o 1 0 0 _ f o l l o w e r import S O 1 0 0 F o l l o w e r C o n f i g
9from lerobot . robots . s o 1 0 0 _ f o l l o w e r . s o 1 0 0 _ f o l l o w e r import S O 1 0 0 F o l l o w e r
10
11M A X _ E P I S O D E S = 5
12M A X _ S T E P S _ P E R _ E P I S O D E = 20
13
14device = torch . device ( " mps " ) # or " cuda " or " cpu "
15m od el _i d = " lerobot / pi0 _b as e "
16
17model = P I 0 P o l i c y . f r o m _ p r e t r a i n e d ( m ode l_ id )
18
19preprocess , p o s t p r o c e s s = m a k e _ p r e _ p o s t _ p r o c e s s o r s (
20model . config ,
21model_id ,
22# This o v e r r i d e s allows to run on MPS , o t h e r w i s e de fa ul ts to CUDA ( if a v a i l a b l e )
23p r e p r o c e s s o r _ o v e r r i d e s ={ " d e v i c e _ p r o c e s s o r " : { " device " : " mps " }} ,
24)
25
26# find ports using lerobot - find - port
27f o l l o w e r _ p o r t = ... # s o m e t h i n g like "/ dev / tty . u s b m o d e m 5 8 7 6 0 4 3 1 6 3 1 "
28
29# the robot ids are used the load the right c a l i b r a t i o n files
30f o l l o w e r _ i d = ... # s o m e t h i n g like " f o l l o w e r _ s o 1 0 0 "
31
32# Robot and e n v i r o n m e n t c o n f i g u r a t i o n
33# Camera keys must match the name and r e s o l u t i o n s of the ones used for t ra in in g !
34# You can check the camera keys e xpe ct ed by a model in the info . json card on the Hub
35c a m e r a _ c o n f i g = {
36" b a s e _ 0 _ r g b " : O p e n C V C a m e r a C o n f i g ( i n d e x _ o r _ p a t h =0 , width =640 , height =480 , fps =30) ,
37" l e f t _ w r i s t _ 0 _ r g b " : O p e n C V C a m e r a C o n f i g ( i n d e x _ o r _ p a t h =1 , width =640 , height =480 , fps =30) ,
38" r i g h t _ w r i s t _ 0 _ r g b " : O p e n C V C a m e r a C o n f i g ( i n d e x _ o r _ p a t h =2 , width =640 , height =480 , fps =30) ,
39}
40
41r o b o t _ c f g = S O 1 0 0 F o l l o w e r C o n f i g ( port = follower_port , id = follower_id , cameras = c a m e r a _ c o n f i g )
42robot = S O 1 0 0 F o l l o w e r ( r o b o t _ c f g )
43robot . connect ()
44
45task = ... # s o m e t h i n g like " pick the red block "
46r o b o t _ t y p e = ... # s o m e t h i n g like " s o 1 0 0 _ f o l l o w e r " for multi - e m b o d i m e n t dat as et s
47
63

[PAGE 64]

Figure 39 | The SmolVLA architecture, as in Shukor et al. (2025). SmolVLA is a compact MoE model trained with flow
matching to denoise action chunks. Vision and language tokens are fed to a VLM backbone, and share information with the
proprioperceptive and action tokens via the attention mechanism. The attention expert interleaves SA and CA layers for
further conditioning on the visual features from the VLM backbone. SmolVLA skips computations and reduces the visual
tokens, resulting in 7x less memory usage thanπ0 (450M parameters vs.π 0’s 3.3B).
48# This is used to match the raw o b s e r v a t i o n keys to the keys ex pe ct ed by the policy
49a c t i o n _ f e a t u r e s = h w _ t o _ d a t a s e t _ f e a t u r e s ( robot . action_features , " action " )
50o b s _ f e a t u r e s = h w _ t o _ d a t a s e t _ f e a t u r e s ( robot . o b s e r v a t i o n _ f e a t u r e s , " o b s e r v a t i o n " )
51d a t a s e t _ f e a t u r e s = {** action_features , ** o b s _ f e a t u r e s }
52
53for _ in range ( M A X _ E P I S O D E S ):
54for _ in range ( M A X _ S T E P S _ P E R _ E P I S O D E ):
55obs = robot . g e t _ o b s e r v a t i o n ()
56o b s _ f r a m e = b u i l d _ i n f e r e n c e _ f r a m e (
57obs , da ta se t_f ea tu re s , device , task = task , r o b o t _ t y p e = r o b o t _ t y p e
58)
59
60obs = p r e p r o c e s s ( o b s _ f r a m e )
61
62action = model . s e l e c t _ a c t i o n ( obs )
63action = p o s t p r o c e s s ( action )
64action = m a k e _ r o b o t _ a c t i o n ( action , d a t a s e t _ f e a t u r e s )
65robot . s e n d _ a c t i o n ( action )
66
67print ( " Episode fi nis he d ! S ta rti ng new episode ... " )
5.4 SmolVLA
With VLAs in the early stage of development compared to more mature LLMs and VLMs, much of the progress
made on VLAs remains proprietary, with many releases exclusively sharing the weights while withholding the data
used, full experimental details and essential methodological components of training. In constrast with this closed
approach, SmolVLA (Shukor et al., 2025) is an entirely open-source research effort, which aims at democratizing
the developments of robotics foundation models by open sourcing the model alongside the data used as well as the
training recipes.
While encouraging efforts likeπ0 (Black et al., 2024) demonstrate the feasibility of open VLA systems, they remain
(1) large and compute-intensive and (2) dependent on closed datasets collected via centralized efforts on costly robotic
platforms, which ultimately hinders the accessibility of the method altogether. SmolVLA mitigates both these issues
by (1) prioritizing a compact, compute-efficient VLA design and (2) targeting community-contributed datasets on
64

[PAGE 65]

accessible robotic platforms such as the SO-100 and SO-101 arms. Similarly toπ0, SmolVLA (Figure 39) employs
a MoE architecture combining a pretrained VLM backbone with a dedicated action expert, and trains with flow
matching. To ensure efficiency and accessibility, SmolVLA adopts SmolVLM-2 (Marafioti et al., 2025) as its VLM
backbone, considering SmolVLM-2’s reduced size and capability to process multiple image inputs alongside text items.
SmolVLM-2 uses SigLIP (Zhai et al., 2023) as vision encoder, producing visual features for a SmolLM2 language
decoder (Allal et al., 2025). Further, SmolVLA adopts a smaller action expert consisting of∼100M parameters and
an interleaved stack of self and cross-attention layers. To improve efficiency, the action expert adopts a reduced
embedding dimension compared to the VLM backbone, resulting indvθ = 0.75dVLM. Shukor et al. (2025)’s design
choices thus result in a much smaller size model compared toπ0, consisting of ca. 450M parameters versusπ0’s 3.3B
parameters.
In practice, SmolVLA consumes multi-view RGB images, a natural-language instruction, and projected sensorimotor
state token as inputs, together with the noisedaction chunk˜at:t+Ha the action expertvθ is trained to denoise. The
robot proprioperceptive states are projected to a shared token space with the VLM to matchdVLM, and successively
projected into the expert’s token space. Similarily toπ0, SmolVLA adopts separate experts communicating exclusively
through self-attention layers, which however do not employ blockwise causal attention masking and rather favour
simple causal masking.
In contrast withπ0, the action expert interleavescross-attention(CA) andself-attention(SA) layers, a choice shown
to yield higher success and smoother action chunks in practice. While in the expert SA layers tokens are used to
obtain queries, keys and values, CA layers use action tokens only as queries, and instead project visual, language
and proprioperceptive tokens from the VLM backbone to a shared embedding space to then obtain keys and values.
Notably, keys and values can be cached here as well, resulting in performance gains at inference time.
SmolVLA also trims down both token and layer compute. First, itreduces visual tokensvia pixel shuffling to a
fixed budget of 64 tokens per frame, foregoing the tiling used during VLM pretraining for the sake of runtime
efficiency. Second, itskips upper VLM layers, as only features from the firstN decoder layers, withN =L/2, are
consumed, which provides a good speed-performance trade-off and effectively halves compute needs for the larger
part of SmolVLA. Beyond model compactness, SmolVLA also contributes an inference stack that decouples action
prediction from execution for responsiveness on modest hardware (Section 4.4).
Departing from reliance on proprietary datasets, SmolVLA pretrains exclusively on 450+community datasets, totaling
20k+ trajectories. Because instructions in community contributed dataset can be noisy or missing, the authors
re-annotate tasks with a small off-the-shelf VLM using frames sampled from the dataset, and standardize camera
viewpoints by mapping sources to a consistent top/wrist/side ordering. At test time, similarily toπ0, SmolVLA
forward-integrates flow over 10 steps, resulting in fast inference. SmolVLA proves effective across a range of both real-
world and simulated environments, rivalingπ0 while being close to 40% faster and consuming 6x less memory (Shukor
et al., 2025).
5.4.1 Code Example: Using SmolVLA
Code 14: Using SmolVLA
https://github.com/fracapuano/robot-learning-tutorial/blob/main/snippets/ch5/02_using_smolvla.py
1import torch
2
3from lerobot . cameras . opencv . c o n f i g u r a t i o n _ o p e n c v import O p e n C V C a m e r a C o n f i g
4from lerobot . da ta set s . utils import h w _ t o _ d a t a s e t _ f e a t u r e s
5from lerobot . po li cie s . factory import m a k e _ p r e _ p o s t _ p r o c e s s o r s
6from lerobot . po li cie s . smolvla . m o d e l i n g _ s m o l v l a import S m o l V L A P o l i c y
7from lerobot . po li cie s . utils import b u i l d _ i n f e r e n c e _ f r a m e , m a k e _ r o b o t _ a c t i o n
8from lerobot . robots . s o 1 0 0 _ f o l l o w e r . c o n f i g _ s o 1 0 0 _ f o l l o w e r import S O 1 0 0 F o l l o w e r C o n f i g
9from lerobot . robots . s o 1 0 0 _ f o l l o w e r . s o 1 0 0 _ f o l l o w e r import S O 1 0 0 F o l l o w e r
10
11M A X _ E P I S O D E S = 5
12M A X _ S T E P S _ P E R _ E P I S O D E = 20
13
14device = torch . device ( " mps " ) # or " cuda " or " cpu "
15m od el _i d = " lerobot / s m o l v l a _ b a s e "
16
65

[PAGE 66]

17model = S m o l V L A P o l i c y . f r o m _ p r e t r a i n e d ( m ode l_ id )
18
19preprocess , p o s t p r o c e s s = m a k e _ p r e _ p o s t _ p r o c e s s o r s (
20model . config ,
21model_id ,
22# This o v e r r i d e s allows to run on MPS , o t h e r w i s e de fa ul ts to CUDA ( if a v a i l a b l e )
23p r e p r o c e s s o r _ o v e r r i d e s ={ " d e v i c e _ p r o c e s s o r " : { " device " : " mps " }} ,
24)
25
26# find ports using lerobot - find - port
27f o l l o w e r _ p o r t = ... # s o m e t h i n g like "/ dev / tty . u s b m o d e m 5 8 7 6 0 4 3 1 6 3 1 "
28
29# the robot ids are used the load the right c a l i b r a t i o n files
30f o l l o w e r _ i d = ... # s o m e t h i n g like " f o l l o w e r _ s o 1 0 0 "
31
32# Robot and e n v i r o n m e n t c o n f i g u r a t i o n
33# Camera keys must match the name and r e s o l u t i o n s of the ones used for t ra in in g !
34# You can check the camera keys e xpe ct ed by a model in the info . json card on the Hub
35c a m e r a _ c o n f i g = {
36" camera1 " : O p e n C V C a m e r a C o n f i g ( i n d e x _ o r _ p a t h =0 , width =640 , height =480 , fps =30) ,
37" camera2 " : O p e n C V C a m e r a C o n f i g ( i n d e x _ o r _ p a t h =1 , width =640 , height =480 , fps =30) ,
38}
39
40r o b o t _ c f g = S O 1 0 0 F o l l o w e r C o n f i g ( port = follower_port , id = follower_id , cameras = c a m e r a _ c o n f i g )
41robot = S O 1 0 0 F o l l o w e r ( r o b o t _ c f g )
42robot . connect ()
43
44task = ... # s o m e t h i n g like " pick the red block "
45r o b o t _ t y p e = ... # s o m e t h i n g like " s o 1 0 0 _ f o l l o w e r " for multi - e m b o d i m e n t dat as et s
46
47# This is used to match the raw o b s e r v a t i o n keys to the keys ex pe ct ed by the policy
48a c t i o n _ f e a t u r e s = h w _ t o _ d a t a s e t _ f e a t u r e s ( robot . action_features , " action " )
49o b s _ f e a t u r e s = h w _ t o _ d a t a s e t _ f e a t u r e s ( robot . o b s e r v a t i o n _ f e a t u r e s , " o b s e r v a t i o n " )
50d a t a s e t _ f e a t u r e s = {** action_features , ** o b s _ f e a t u r e s }
51
52for _ in range ( M A X _ E P I S O D E S ):
53for _ in range ( M A X _ S T E P S _ P E R _ E P I S O D E ):
54obs = robot . g e t _ o b s e r v a t i o n ()
55o b s _ f r a m e = b u i l d _ i n f e r e n c e _ f r a m e (
56obs , da ta se t_f ea tu re s , device , task = task , r o b o t _ t y p e = r o b o t _ t y p e
57)
58
59obs = p r e p r o c e s s ( o b s _ f r a m e )
60
61action = model . s e l e c t _ a c t i o n ( obs )
62action = p o s t p r o c e s s ( action )
63action = m a k e _ r o b o t _ a c t i o n ( action , d a t a s e t _ f e a t u r e s )
64robot . s e n d _ a c t i o n ( action )
65
66print ( " Episode fi nis he d ! S ta rti ng new episode ... " )
66

[PAGE 67]

6 Conclusions
This tutorial has charted the paradigmatic shift transforming robotics, tracing the evolution of robotics from
structured, model-based methods to the dynamic, data-driven approaches that define modern robot learning. We
began by examining the limitations of traditional dynamics-based control, namely its brittleness and significant
engineering overhead, which motivate the adoption of more flexible, learning-based alternatives. Unlike scalable,
data-driven techniques, conventional explicit models demand extensive human expertise, hindering wider accessibility
and scalability of robotics.
Our exploration traced a clear trajectory of progress, beginning with Reinforcement Learning (RL). While RL offers
a powerful paradigm for learning through interaction, its application in robotics is complicated by challenges such
as sample inefficiency, safety concerns in real-world training, and the complexities of reward design. We saw how
modern approaches like HIL-SERL make real-world RL more feasible by incorporating training-time human guidance,
datasets of previously collected data as well as learned reward classifiers.
Nonetheless, the inherent difficulties of RL increasingly motivate approaches based on imitation learning, capable to
safely learns from limited numbers of real-world, reward-free expert demonstrations. In turn, the wider adoption of
imitation learning led to the development of single-task policies, where advanced Behavioral Cloning techniques—
implementedasstate-conditionedgenerativemodelslikeActionChunkingwithTransformersandDiffusionPolicy—have
demonstrated the ability to learn complex, multimodal behaviors from human demonstrations. These advancements
laid the groundwork for the current frontier: generalist, language-conditioned Vision-Language-Action models capable
to perform few- and zero-shot a variety of different real-world tasks. By leveraging powerful pre-trained backbones
and sophisticated generative methods like flow matching, models such asπ0 and SmolVLA represent a significant leap
towards foundational models for robotics capable of generalizing across diverse tasks, and even robot embodiments.
A central theme of this work is the critical role of openness in accelerating this progress. The recent explosion in
capability is inseparable from the advent of large-scale, openly available datasets, standardized, stable and accessible
model architectures, and accessible, open-source software likelerobot. We argue this convergence on open-source
robotics is not a mere trend but a fundamental enabler, democratizing access to research and unlocking the potential
of large, decentralized efforts to advance the field.
The journey detailed in this tutorial, from first principles to the state-of-the-art, aims to equip researchers and
practitioners with the context and tools to begin their own explorations in open-source robot learning.
References
Joshua Achiam. Spinning up in deep reinforcement learning. 2018.
Pulkit Agrawal. Computational Sensorimotor Learning.
Ilge Akkaya, Marcin Andrychowicz, Maciek Chociej, Mateusz Litwin, Bob McGrew, Arthur Petron, Alex Paino, Matthias
Plappert, Glenn Powell, Raphael Ribas, Jonas Schneider, Nikolas Tezak, Jerry Tworek, Peter Welinder, Lilian Weng, Qiming
Yuan, Wojciech Zaremba, and Lei Zhang. Solving Rubik’s Cube with a Robot Hand, October 2019.
Jean-Baptiste Alayrac, Jeff Donahue, Pauline Luc, Antoine Miech, Iain Barr, Yana Hasson, Karel Lenc, Arthur Mensch, Katie
Millican, Malcolm Reynolds, Roman Ring, Eliza Rutherford, Serkan Cabi, Tengda Han, Zhitao Gong, Sina Samangooei,
Marianne Monteiro, Jacob Menick, Sebastian Borgeaud, Andrew Brock, Aida Nematzadeh, Sahand Sharifzadeh, Mikolaj
Binkowski, Ricardo Barreira, Oriol Vinyals, Andrew Zisserman, and Karen Simonyan. Flamingo: A Visual Language Model
for Few-Shot Learning, November 2022.
Jorge Aldaco, Travis Armstrong, Robert Baruch, Jeff Bingham, Sanky Chan, Debidatta Dwibedi, Chelsea Finn, Pete Florence,
Spencer Goodrich, Wayne Gramlich, Alexander Herzog, Jonathan Hoech, Thinh Nguyen, Ian Storz, Baruch Tabanpour,
Jonathan Tompson, Ayzaan Wahid, Ted Wahrburg, Sichun Xu, Sergey Yaroshenko, and Tony Z Zhao. ALOHA 2: An
Enhanced Low-Cost Hardware for Bimanual Teleoperation.
Mohammad Alizadeh and Zheng H. Zhu. A comprehensive survey of space robotic manipulators for on-orbit servicing.Frontiers
in Robotics and AI, 11, October 2024. ISSN 2296-9144. doi: 10.3389/frobt.2024.1470950.
Loubna Ben Allal, Anton Lozhkov, Elie Bakouch, Gabriel Martín Blázquez, Guilherme Penedo, Lewis Tunstall, Andrés
Marafioti, Hynek Kydlíček, Agustín Piqueres Lajarín, Vaibhav Srivastav, Joshua Lochner, Caleb Fahlgren, Xuan-Son Nguyen,
Clémentine Fourrier, Ben Burtenshaw, Hugo Larcher, Haojun Zhao, Cyril Zakka, Mathieu Morlon, Colin Raffel, Leandro von
Werra, and Thomas Wolf. SmolLM2: When Smol Goes Big – Data-Centric Training of a Small Language Model, February
2025.
67

[PAGE 68]

Rika Antonova, Silvia Cruciani, Christian Smith, and Danica Kragic. Reinforcement Learning for Pivoting Task, March 2017.
Shuai Bai, Keqin Chen, Xuejing Liu, Jialin Wang, Wenbin Ge, Sibo Song, Kai Dang, Peng Wang, Shijie Wang, Jun Tang,
Humen Zhong, Yuanzhi Zhu, Mingkun Yang, Zhaohai Li, Jianqiang Wan, Pengfei Wang, Wei Ding, Zheren Fu, Yiheng Xu,
Jiabo Ye, Xi Zhang, Tianbao Xie, Zesen Cheng, Hang Zhang, Zhibo Yang, Haiyang Xu, and Junyang Lin. Qwen2.5-VL
technical report, 2025.
Philip J. Ball, Laura Smith, Ilya Kostrikov, and Sergey Levine. Efficient Online Reinforcement Learning with Offline Data,
May 2023.
Kostas E. Bekris, Joe Doerr, Patrick Meng, and Sumanth Tangirala. The State of Robot Motion Generation, October 2024.
Marc G. Bellemare, Salvatore Candido, Pablo Samuel Castro, Jun Gong, Marlos C. Machado, Subhodeep Moitra, Sameera S.
Ponda, and Ziyu Wang. Autonomous navigation of stratospheric balloons using reinforcement learning.Nature, 588(7836):
77–82, December 2020. ISSN 1476-4687. doi: 10.1038/s41586-020-2939-8.
Richard Bellman. A Markovian Decision Process.Journal of Mathematics and Mechanics, 6(5):679–684, 1957. ISSN 0095-9057.
Johan Bjorck, Fernando Castañeda, Nikita Cherniadev, Xingye Da, Runyu Ding, Linxi "Jim" Fan, Yu Fang, Dieter Fox,
Fengyuan Hu, Spencer Huang, Joel Jang, Zhenyu Jiang, Jan Kautz, Kaushil Kundalia, Lawrence Lao, Zhiqi Li, Zongyu
Lin, Kevin Lin, Guilin Liu, Edith Llontop, Loic Magne, Ajay Mandlekar, Avnish Narayan, Soroush Nasiriany, Scott Reed,
You Liang Tan, Guanzhi Wang, Zu Wang, Jing Wang, Qi Wang, Jiannan Xiang, Yuqi Xie, Yinzhen Xu, Zhenjia Xu,
Seonghyeon Ye, Zhiding Yu, Ao Zhang, Hao Zhang, Yizhou Zhao, Ruijie Zheng, and Yuke Zhu. GR00T N1: An Open
Foundation Model for Generalist Humanoid Robots, March 2025.
Kevin Black, Noah Brown, Danny Driess, Adnan Esmail, Michael Equi, Chelsea Finn, Niccolo Fusai, Lachy Groom, Karol
Hausman, Brian Ichter, Szymon Jakubczak, Tim Jones, Liyiming Ke, Sergey Levine, Adrian Li-Bell, Mohith Mothukuri,
Suraj Nair, Karl Pertsch, Lucy Xiaoyang Shi, James Tanner, Quan Vuong, Anna Walling, Haohuan Wang, and Ury Zhilinsky.
$π_0$: A Vision-Language-Action Flow Model for General Robot Control, October 2024.
Anthony Brohan, Noah Brown, Justice Carbajal, Yevgen Chebotar, Xi Chen, Krzysztof Choromanski, Tianli Ding, Danny
Driess, Avinava Dubey, Chelsea Finn, Pete Florence, Chuyuan Fu, Montse Gonzalez Arenas, Keerthana Gopalakrishnan,
Kehang Han, Karol Hausman, Alexander Herzog, Jasmine Hsu, Brian Ichter, Alex Irpan, Nikhil Joshi, Ryan Julian, Dmitry
Kalashnikov, Yuheng Kuang, Isabel Leal, Lisa Lee, Tsang-Wei Edward Lee, Sergey Levine, Yao Lu, Henryk Michalewski,
Igor Mordatch, Karl Pertsch, Kanishka Rao, Krista Reymann, Michael Ryoo, Grecia Salazar, Pannag Sanketi, Pierre
Sermanet, Jaspiar Singh, Anikait Singh, Radu Soricut, Huong Tran, Vincent Vanhoucke, Quan Vuong, Ayzaan Wahid,
Stefan Welker, Paul Wohlhart, Jialin Wu, Fei Xia, Ted Xiao, Peng Xu, Sichun Xu, Tianhe Yu, and Brianna Zitkovich. RT-2:
Vision-Language-Action Models Transfer Web Knowledge to Robotic Control, July 2023a.
Anthony Brohan, Noah Brown, Justice Carbajal, Yevgen Chebotar, Joseph Dabis, Chelsea Finn, Keerthana Gopalakrishnan,
Karol Hausman, Alex Herzog, Jasmine Hsu, Julian Ibarz, Brian Ichter, Alex Irpan, Tomas Jackson, Sally Jesmonth, Nikhil J.
Joshi, Ryan Julian, Dmitry Kalashnikov, Yuheng Kuang, Isabel Leal, Kuang-Huei Lee, Sergey Levine, Yao Lu, Utsav Malla,
Deeksha Manjunath, Igor Mordatch, Ofir Nachum, Carolina Parada, Jodilyn Peralta, Emily Perez, Karl Pertsch, Jornell
Quiambao, Kanishka Rao, Michael Ryoo, Grecia Salazar, Pannag Sanketi, Kevin Sayed, Jaspiar Singh, Sumedh Sontakke,
Austin Stone, Clayton Tan, Huong Tran, Vincent Vanhoucke, Steve Vega, Quan Vuong, Fei Xia, Ted Xiao, Peng Xu, Sichun
Xu, Tianhe Yu, and Brianna Zitkovich. RT-1: Robotics Transformer for Real-World Control at Scale, August 2023b.
Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav
Shyam, Girish Sastry, Amanda Askell, Sandhini Agarwal, Ariel Herbert-Voss, Gretchen Krueger, Tom Henighan, Rewon
Child, Aditya Ramesh, Daniel M. Ziegler, Jeffrey Wu, Clemens Winter, Christopher Hesse, Mark Chen, Eric Sigler, Mateusz
Litwin, Scott Gray, Benjamin Chess, Jack Clark, Christopher Berner, Sam McCandlish, Alec Radford, Ilya Sutskever, and
Dario Amodei. Language Models are Few-Shot Learners, July 2020.
Minwoo Byeon, Beomhee Park, Haecheon Kim, Sungjun Lee, Woonhyuk Baek, and Saehoon Kim. COYO-700M: Image-text
pair dataset, 2022.
Yevgen Chebotar, Ankur Handa, Viktor Makoviychuk, Miles Macklin, Jan Issac, Nathan Ratliff, and Dieter Fox. Closing
the sim-to-real loop: Adapting simulation randomization with real world experience. In2019 International Conference on
Robotics and Automation (ICRA), pages 8973–8979. IEEE, 2019.
Xi Chen, Josip Djolonga, Piotr Padlewski, Basil Mustafa, Soravit Changpinyo, Jialin Wu, Carlos Riquelme Ruiz, Sebastian
Goodman, Xiao Wang, Yi Tay, Siamak Shakeri, Mostafa Dehghani, Daniel Salz, Mario Lucic, Michael Tschannen, Arsha
Nagrani, Hexiang Hu, Mandar Joshi, Bo Pang, Ceslee Montgomery, Paulina Pietrzyk, Marvin Ritter, A. J. Piergiovanni,
Matthias Minderer, Filip Pavetic, Austin Waters, Gang Li, Ibrahim Alabdulmohsin, Lucas Beyer, Julien Amelot, Kenton Lee,
Andreas Peter Steiner, Yang Li, Daniel Keysers, Anurag Arnab, Yuanzhong Xu, Keran Rong, Alexander Kolesnikov, Mojtaba
Seyedhosseini, Anelia Angelova, Xiaohua Zhai, Neil Houlsby, and Radu Soricut. PaLI-X: On Scaling up a Multilingual Vision
and Language Model, May 2023.
68

[PAGE 69]

Cheng Chi, Zhenjia Xu, Siyuan Feng, Eric Cousineau, Yilun Du, Benjamin Burchfiel, Russ Tedrake, and Shuran Song. Diffusion
Policy: Visuomotor Policy Learning via Action Diffusion, March 2024.
Jonathan H. Connell and Sridhar Mahadevan, editors.Robot Learning. Springer US, Boston, MA, 1993. ISBN 978-1-4613-6396-5
978-1-4615-3184-5. doi: 10.1007/978-1-4615-3184-5.
Wenliang Dai, Junnan Li, Dongxu Li, Anthony Tiong, Junqi Zhao, Weisheng Wang, Boyang Li, Pascale Fung, and Steven Hoi.
InstructBLIP: Towards general-purpose vision-language models with instruction tuning. InThirty-Seventh Conference on
Neural Information Processing Systems, 2023.
Jonas Degrave, Federico Felici, Jonas Buchli, Michael Neunert, Brendan Tracey, Francesco Carpanese, Timo Ewalds, Roland
Hafner, Abbas Abdolmaleki, Diego de las Casas, Craig Donner, Leslie Fritz, Cristian Galperti, Andrea Huber, James Keeling,
Maria Tsimpoukelli, Jackie Kay, Antoine Merle, Jean-Marc Moret, Seb Noury, Federico Pesamosca, David Pfau, Olivier
Sauter, Cristian Sommariva, Stefano Coda, Basil Duval, Ambrogio Fasoli, Pushmeet Kohli, Koray Kavukcuoglu, Demis
Hassabis, and Martin Riedmiller. Magnetic control of tokamak plasmas through deep reinforcement learning.Nature, 602
(7897):414–419, February 2022. ISSN 1476-4687. doi: 10.1038/s41586-021-04301-9.
J. Deng, K. Li, M. Do, H. Su, and L. Fei-Fei. Construction and analysis of a large scale image ontology. Vision Sciences Society,
2009.
Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. BERT: Pre-training of Deep Bidirectional Transformers
for Language Understanding, May 2019.
Danny Driess, Fei Xia, Mehdi S. M. Sajjadi, Corey Lynch, Aakanksha Chowdhery, Brian Ichter, Ayzaan Wahid, Jonathan
Tompson, Quan Vuong, Tianhe Yu, Wenlong Huang, Yevgen Chebotar, Pierre Sermanet, Daniel Duckworth, Sergey Levine,
Vincent Vanhoucke, Karol Hausman, Marc Toussaint, Klaus Greff, Andy Zeng, Igor Mordatch, and Pete Florence. PaLM-E:
An Embodied Multimodal Language Model, March 2023.
Danny Driess, Jost Tobias Springenberg, Brian Ichter, Lili Yu, Adrian Li-Bell, Karl Pertsch, Allen Z. Ren, Homer Walke, Quan
Vuong, Lucy Xiaoyang Shi, and Sergey Levine. Knowledge Insulating Vision-Language-Action Models: Train Fast, Run Fast,
Generalize Better, May 2025.
Patrick Esser, Sumith Kulal, Andreas Blattmann, Rahim Entezari, Jonas Müller, Harry Saini, Yam Levi, Dominik Lorenz,
Axel Sauer, Frederic Boesel, Dustin Podell, Tim Dockhorn, Zion English, Kyle Lacey, Alex Goodwin, Yannik Marek, and
Robin Rombach. Scaling Rectified Flow Transformers for High-Resolution Image Synthesis, March 2024.
William Fedus, Jeff Dean, and Barret Zoph. A Review of Sparse Expert Models in Deep Learning, September 2022.
Enrico Fini, Mustafa Shukor, Xiujun Li, Philipp Dufter, Michal Klein, David Haldimann, Sai Aitharaju, Victor Guilherme Turrisi
da Costa, Louis Béthune, Zhe Gan, Alexander T. Toshev, Marcin Eichner, Moin Nabi, Yinfei Yang, Joshua M. Susskind, and
Alaaeldin El-Nouby. Multimodal Autoregressive Pre-training of Large Vision Encoders, November 2024.
Pete Florence, Corey Lynch, Andy Zeng, Oscar A. Ramirez, Ayzaan Wahid, Laura Downs, Adrian Wong, Johnny Lee, Igor
Mordatch, and Jonathan Tompson. Implicit Behavioral Cloning. InProceedings of the 5th Conference on Robot Learning,
pages 158–168. PMLR, January 2022.
Jun Fujita, Daisuke Soda, Chotaro Murata, and Hiroyuki Tsuhari. Development of Robots for Nuclear Power Plants and Their
Application to New Fields. 57(4), 2020.
Aaron Grattafiori, Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman,
Akhil Mathur, Alan Schelten, Alex Vaughan, Amy Yang, Angela Fan, Anirudh Goyal, Anthony Hartshorn, Aobo Yang,
Archi Mitra, Archie Sravankumar, Artem Korenev, Arthur Hinsvark, Arun Rao, Aston Zhang, Aurelien Rodriguez, Austen
Gregerson, Ava Spataru, Baptiste Roziere, Bethany Biron, Binh Tang, Bobbie Chern, Charlotte Caucheteux, Chaya Nayak,
Chloe Bi, Chris Marra, Chris McConnell, Christian Keller, Christophe Touret, Chunyang Wu, Corinne Wong, Cristian Canton
Ferrer, Cyrus Nikolaidis, Damien Allonsius, Daniel Song, Danielle Pintz, Danny Livshits, Danny Wyatt, David Esiobu,
Dhruv Choudhary, Dhruv Mahajan, Diego Garcia-Olano, Diego Perino, Dieuwke Hupkes, Egor Lakomkin, Ehab AlBadawy,
Elina Lobanova, Emily Dinan, Eric Michael Smith, Filip Radenovic, Francisco Guzmán, Frank Zhang, Gabriel Synnaeve,
Gabrielle Lee, Georgia Lewis Anderson, Govind Thattai, Graeme Nail, Gregoire Mialon, Guan Pang, Guillem Cucurell,
Hailey Nguyen, Hannah Korevaar, Hu Xu, Hugo Touvron, Iliyan Zarov, Imanol Arrieta Ibarra, Isabel Kloumann, Ishan
Misra, Ivan Evtimov, Jack Zhang, Jade Copet, Jaewon Lee, Jan Geffert, Jana Vranes, Jason Park, Jay Mahadeokar, Jeet
Shah, Jelmer van der Linde, Jennifer Billock, Jenny Hong, Jenya Lee, Jeremy Fu, Jianfeng Chi, Jianyu Huang, Jiawen Liu,
Jie Wang, Jiecao Yu, Joanna Bitton, Joe Spisak, Jongsoo Park, Joseph Rocca, Joshua Johnstun, Joshua Saxe, Junteng
Jia, Kalyan Vasuden Alwala, Karthik Prasad, Kartikeya Upasani, Kate Plawiak, Ke Li, Kenneth Heafield, Kevin Stone,
Khalid El-Arini, Krithika Iyer, Kshitiz Malik, Kuenley Chiu, Kunal Bhalla, Kushal Lakhotia, Lauren Rantala-Yeary, Laurens
van der Maaten, Lawrence Chen, Liang Tan, Liz Jenkins, Louis Martin, Lovish Madaan, Lubo Malo, Lukas Blecher, Lukas
Landzaat, Luke de Oliveira, Madeline Muzzi, Mahesh Pasupuleti, Mannat Singh, Manohar Paluri, Marcin Kardas, Maria
69

[PAGE 70]

Tsimpoukelli, Mathew Oldham, Mathieu Rita, Maya Pavlova, Melanie Kambadur, Mike Lewis, Min Si, Mitesh Kumar Singh,
Mona Hassan, Naman Goyal, Narjes Torabi, Nikolay Bashlykov, Nikolay Bogoychev, Niladri Chatterji, Ning Zhang, Olivier
Duchenne, Onur Çelebi, Patrick Alrassy, Pengchuan Zhang, Pengwei Li, Petar Vasic, Peter Weng, Prajjwal Bhargava, Pratik
Dubal, Praveen Krishnan, Punit Singh Koura, Puxin Xu, Qing He, Qingxiao Dong, Ragavan Srinivasan, Raj Ganapathy,
Ramon Calderer, Ricardo Silveira Cabral, Robert Stojnic, Roberta Raileanu, Rohan Maheswari, Rohit Girdhar, Rohit Patel,
Romain Sauvestre, Ronnie Polidoro, Roshan Sumbaly, Ross Taylor, Ruan Silva, Rui Hou, Rui Wang, Saghar Hosseini, Sahana
Chennabasappa, Sanjay Singh, Sean Bell, Seohyun Sonia Kim, Sergey Edunov, Shaoliang Nie, Sharan Narang, Sharath
Raparthy, Sheng Shen, Shengye Wan, Shruti Bhosale, Shun Zhang, Simon Vandenhende, Soumya Batra, Spencer Whitman,
Sten Sootla, Stephane Collot, Suchin Gururangan, Sydney Borodinsky, Tamar Herman, Tara Fowler, Tarek Sheasha, Thomas
Georgiou, Thomas Scialom, Tobias Speckbacher, Todor Mihaylov, Tong Xiao, Ujjwal Karn, Vedanuj Goswami, Vibhor Gupta,
Vignesh Ramanathan, Viktor Kerkez, Vincent Gonguet, Virginie Do, Vish Vogeti, Vítor Albiero, Vladan Petrovic, Weiwei
Chu, Wenhan Xiong, Wenyin Fu, Whitney Meers, Xavier Martinet, Xiaodong Wang, Xiaofang Wang, Xiaoqing Ellen Tan,
Xide Xia, Xinfeng Xie, Xuchao Jia, Xuewei Wang, Yaelle Goldschlag, Yashesh Gaur, Yasmine Babaei, Yi Wen, Yiwen Song,
Yuchen Zhang, Yue Li, Yuning Mao, Zacharie Delpierre Coudert, Zheng Yan, Zhengxing Chen, Zoe Papakipos, Aaditya
Singh, Aayushi Srivastava, Abha Jain, Adam Kelsey, Adam Shajnfeld, Adithya Gangidi, Adolfo Victoria, Ahuva Goldstand,
Ajay Menon, Ajay Sharma, Alex Boesenberg, Alexei Baevski, Allie Feinstein, Amanda Kallet, Amit Sangani, Amos Teo,
Anam Yunus, Andrei Lupu, Andres Alvarado, Andrew Caples, Andrew Gu, Andrew Ho, Andrew Poulton, Andrew Ryan,
Ankit Ramchandani, Annie Dong, Annie Franco, Anuj Goyal, Aparajita Saraf, Arkabandhu Chowdhury, Ashley Gabriel,
Ashwin Bharambe, Assaf Eisenman, Azadeh Yazdan, Beau James, Ben Maurer, Benjamin Leonhardi, Bernie Huang, Beth
Loyd, Beto De Paola, Bhargavi Paranjape, Bing Liu, Bo Wu, Boyu Ni, Braden Hancock, Bram Wasti, Brandon Spence,
Brani Stojkovic, Brian Gamido, Britt Montalvo, Carl Parker, Carly Burton, Catalina Mejia, Ce Liu, Changhan Wang,
Changkyu Kim, Chao Zhou, Chester Hu, Ching-Hsiang Chu, Chris Cai, Chris Tindal, Christoph Feichtenhofer, Cynthia
Gao, Damon Civin, Dana Beaty, Daniel Kreymer, Daniel Li, David Adkins, David Xu, Davide Testuggine, Delia David,
Devi Parikh, Diana Liskovich, Didem Foss, Dingkang Wang, Duc Le, Dustin Holland, Edward Dowling, Eissa Jamil, Elaine
Montgomery, Eleonora Presani, Emily Hahn, Emily Wood, Eric-Tuan Le, Erik Brinkman, Esteban Arcaute, Evan Dunbar,
Evan Smothers, Fei Sun, Felix Kreuk, Feng Tian, Filippos Kokkinos, Firat Ozgenel, Francesco Caggioni, Frank Kanayet,
Frank Seide, Gabriela Medina Florez, Gabriella Schwarz, Gada Badeer, Georgia Swee, Gil Halpern, Grant Herman, Grigory
Sizov, Guangyi, Zhang, Guna Lakshminarayanan, Hakan Inan, Hamid Shojanazeri, Han Zou, Hannah Wang, Hanwen Zha,
Haroun Habeeb, Harrison Rudolph, Helen Suk, Henry Aspegren, Hunter Goldman, Hongyuan Zhan, Ibrahim Damlaj, Igor
Molybog, Igor Tufanov, Ilias Leontiadis, Irina-Elena Veliche, Itai Gat, Jake Weissman, James Geboski, James Kohli, Janice
Lam, Japhet Asher, Jean-Baptiste Gaya, Jeff Marcus, Jeff Tang, Jennifer Chan, Jenny Zhen, Jeremy Reizenstein, Jeremy
Teboul, Jessica Zhong, Jian Jin, Jingyi Yang, Joe Cummings, Jon Carvill, Jon Shepard, Jonathan McPhie, Jonathan Torres,
Josh Ginsburg, Junjie Wang, Kai Wu, Kam Hou U, Karan Saxena, Kartikay Khandelwal, Katayoun Zand, Kathy Matosich,
Kaushik Veeraraghavan, Kelly Michelena, Keqian Li, Kiran Jagadeesh, Kun Huang, Kunal Chawla, Kyle Huang, Lailin
Chen, Lakshya Garg, Lavender A, Leandro Silva, Lee Bell, Lei Zhang, Liangpeng Guo, Licheng Yu, Liron Moshkovich, Luca
Wehrstedt, Madian Khabsa, Manav Avalani, Manish Bhatt, Martynas Mankus, Matan Hasson, Matthew Lennie, Matthias
Reso, Maxim Groshev, Maxim Naumov, Maya Lathi, Meghan Keneally, Miao Liu, Michael L. Seltzer, Michal Valko, Michelle
Restrepo, Mihir Patel, Mik Vyatskov, Mikayel Samvelyan, Mike Clark, Mike Macey, Mike Wang, Miquel Jubert Hermoso,
Mo Metanat, Mohammad Rastegari, Munish Bansal, Nandhini Santhanam, Natascha Parks, Natasha White, Navyata Bawa,
Nayan Singhal, Nick Egebo, Nicolas Usunier, Nikhil Mehta, Nikolay Pavlovich Laptev, Ning Dong, Norman Cheng, Oleg
Chernoguz, Olivia Hart, Omkar Salpekar, Ozlem Kalinli, Parkin Kent, Parth Parekh, Paul Saab, Pavan Balaji, Pedro Rittner,
Philip Bontrager, Pierre Roux, Piotr Dollar, Polina Zvyagina, Prashant Ratanchandani, Pritish Yuvraj, Qian Liang, Rachad
Alao, Rachel Rodriguez, Rafi Ayub, Raghotham Murthy, Raghu Nayani, Rahul Mitra, Rangaprabhu Parthasarathy, Raymond
Li, Rebekkah Hogan, Robin Battey, Rocky Wang, Russ Howes, Ruty Rinott, Sachin Mehta, Sachin Siby, Sai Jayesh Bondu,
Samyak Datta, Sara Chugh, Sara Hunt, Sargun Dhillon, Sasha Sidorov, Satadru Pan, Saurabh Mahajan, Saurabh Verma,
Seiji Yamamoto, Sharadh Ramaswamy, Shaun Lindsay, Shaun Lindsay, Sheng Feng, Shenghao Lin, Shengxin Cindy Zha,
Shishir Patil, Shiva Shankar, Shuqiang Zhang, Shuqiang Zhang, Sinong Wang, Sneha Agarwal, Soji Sajuyigbe, Soumith
Chintala, Stephanie Max, Stephen Chen, Steve Kehoe, Steve Satterfield, Sudarshan Govindaprasad, Sumit Gupta, Summer
Deng, Sungmin Cho, Sunny Virk, Suraj Subramanian, Sy Choudhury, Sydney Goldman, Tal Remez, Tamar Glaser, Tamara
Best, Thilo Koehler, Thomas Robinson, Tianhe Li, Tianjun Zhang, Tim Matthews, Timothy Chou, Tzook Shaked, Varun
Vontimitta, Victoria Ajayi, Victoria Montanez, Vijai Mohan, Vinay Satish Kumar, Vishal Mangla, Vlad Ionescu, Vlad
Poenaru, Vlad Tiberiu Mihailescu, Vladimir Ivanov, Wei Li, Wenchen Wang, Wenwen Jiang, Wes Bouaziz, Will Constable,
Xiaocheng Tang, Xiaojian Wu, Xiaolan Wang, Xilun Wu, Xinbo Gao, Yaniv Kleinman, Yanjun Chen, Ye Hu, Ye Jia, Ye Qi,
Yenda Li, Yilin Zhang, Ying Zhang, Yossi Adi, Youngjin Nam, Yu, Wang, Yu Zhao, Yuchen Hao, Yundi Qian, Yunlu Li,
Yuzi He, Zach Rait, Zachary DeVito, Zef Rosnbrick, Zhaoduo Wen, Zhenyu Yang, Zhiwei Zhao, and Zhiyu Ma. The Llama 3
Herd of Models, November 2024.
Robert J. Griffin, Georg Wiedebach, Sylvain Bertrand, Alexander Leonessa, and Jerry Pratt. Walking Stabilization Using
Step Timing and Location Adjustment on the Humanoid Robot, Atlas. In2017 IEEE/RSJ International Conference on
Intelligent Robots and Systems (IROS), pages 667–673, September 2017. doi: 10.1109/IROS.2017.8202223.
Tuomas Haarnoja, Haoran Tang, Pieter Abbeel, and Sergey Levine. Reinforcement Learning with Deep Energy-Based Policies.
InProceedings of the 34th International Conference on Machine Learning, pages 1352–1361. PMLR, July 2017.
70

[PAGE 71]

Tuomas Haarnoja, Aurick Zhou, Pieter Abbeel, and Sergey Levine. Soft Actor-Critic: Off-Policy Maximum Entropy Deep
Reinforcement Learning with a Stochastic Actor, August 2018.
Nicklas Hansen, Xiaolong Wang, and Hao Su. Temporal Difference Learning for Model Predictive Control, July 2022.
Nicolas Heess, Dhruva TB, Srinivasan Sriram, Jay Lemmon, Josh Merel, Greg Wayne, Yuval Tassa, Tom Erez, Ziyu Wang,
S. M. Ali Eslami, Martin Riedmiller, and David Silver. Emergence of Locomotion Behaviours in Rich Environments, July
2017.
Irina Higgins, Loic Matthey, Arka Pal, Christopher Burgess, Xavier Glorot, Matthew Botvinick, Shakir Mohamed, and
Alexander Lerchner. Beta-vae: Learning basic visual concepts with a constrained variational framework. InInternational
Conference on Learning Representations, 2017.
Jonathan Ho, Ajay Jain, and Pieter Abbeel. Denoising Diffusion Probabilistic Models, December 2020.
Eric Jang, Alex Irpan, Mohi Khansari, Daniel Kappler, Frederik Ebert, Corey Lynch, Sergey Levine, and Chelsea Finn. BC-Z:
Zero-Shot Task Generalization with Robotic Imitation Learning, February 2022.
Michael Janner, Yilun Du, Joshua B. Tenenbaum, and Sergey Levine. Planning with Diffusion for Flexible Behavior Synthesis,
December 2022.
Yandong Ji, Gabriel B. Margolis, and Pulkit Agrawal. DribbleBot: Dynamic Legged Manipulation in the Wild, April 2023.
Albert Q. Jiang, Alexandre Sablayrolles, Arthur Mensch, Chris Bamford, Devendra Singh Chaplot, Diego de las Casas, Florian
Bressand, Gianna Lengyel, Guillaume Lample, Lucile Saulnier, Lélio Renard Lavaud, Marie-Anne Lachaux, Pierre Stock,
Teven Le Scao, Thibaut Lavril, Thomas Wang, Timothée Lacroix, and William El Sayed. Mistral 7B, October 2023.
Liyiming Ke, Jingqiang Wang, Tapomayukh Bhattacharjee, Byron Boots, and Siddhartha Srinivasa. Grasping with Chopsticks:
Combating Covariate Shift in Model-free Imitation Learning for Fine Manipulation, November 2020.
Alexander Khazatsky, Karl Pertsch, Suraj Nair, Ashwin Balakrishna, Sudeep Dasari, Siddharth Karamcheti, Soroush Nasiriany,
Mohan Kumar Srirama, Lawrence Yunliang Chen, Kirsty Ellis, Peter David Fagan, Joey Hejna, Masha Itkina, Marion Lepert,
Yecheng Jason Ma, Patrick Tree Miller, Jimmy Wu, Suneel Belkhale, Shivin Dass, Huy Ha, Arhan Jain, Abraham Lee,
Youngwoon Lee, Marius Memmel, Sungjae Park, Ilija Radosavovic, Kaiyuan Wang, Albert Zhan, Kevin Black, Cheng Chi,
Kyle Beltran Hatch, Shan Lin, Jingpei Lu, Jean Mercat, Abdul Rehman, Pannag R. Sanketi, Archit Sharma, Cody Simpson,
Quan Vuong, Homer Rich Walke, Blake Wulfe, Ted Xiao, Jonathan Heewon Yang, Arefeh Yavary, Tony Z. Zhao, Christopher
Agia, Rohan Baijal, Mateo Guaman Castro, Daphne Chen, Qiuyu Chen, Trinity Chung, Jaimyn Drake, Ethan Paul Foster,
Jensen Gao, Vitor Guizilini, David Antonio Herrera, Minho Heo, Kyle Hsu, Jiaheng Hu, Muhammad Zubair Irshad, Donovon
Jackson, Charlotte Le, Yunshuang Li, Kevin Lin, Roy Lin, Zehan Ma, Abhiram Maddukuri, Suvir Mirchandani, Daniel
Morton, Tony Nguyen, Abigail O’Neill, Rosario Scalise, Derick Seale, Victor Son, Stephen Tian, Emi Tran, Andrew E.
Wang, Yilin Wu, Annie Xie, Jingyun Yang, Patrick Yin, Yunchu Zhang, Osbert Bastani, Glen Berseth, Jeannette Bohg, Ken
Goldberg, Abhinav Gupta, Abhishek Gupta, Dinesh Jayaraman, Joseph J. Lim, Jitendra Malik, Roberto Martín-Martín,
Subramanian Ramamoorthy, Dorsa Sadigh, Shuran Song, Jiajun Wu, Michael C. Yip, Yuke Zhu, Thomas Kollar, Sergey
Levine, and Chelsea Finn. DROID: A Large-Scale In-The-Wild Robot Manipulation Dataset, April 2025.
Moo Jin Kim, Karl Pertsch, Siddharth Karamcheti, Ted Xiao, Ashwin Balakrishna, Suraj Nair, Rafael Rafailov, Ethan Foster,
Grace Lam, Pannag Sanketi, Quan Vuong, Thomas Kollar, Benjamin Burchfiel, Russ Tedrake, Dorsa Sadigh, Sergey Levine,
Percy Liang, and Chelsea Finn. OpenVLA: An Open-Source Vision-Language-Action Model, September 2024.
Diederik P Kingma and Max Welling. Auto-encoding variational bayes.arXiv preprint arXiv:1312.6114, 2013.
Rob Knight, Pepijn Kooijmans, Thomas Wolf, Simon Alibert, Michel Aractingi, Dana Aubakirova, Adil Zouitine, Russi Martino,
Steven Palma, Caroline Pascal, and Remi Cadene. Standard Open SO-100 & SO-101 Arms.
Jens Kober, J Andrew Bagnell, and Jan Peters. Reinforcement Learning in Robotics: A Survey.
Jing Yu Koh, Ruslan Salakhutdinov, and Daniel Fried. Grounding language models to images for multimodal inputs and
outputs, 2023.
Zhifeng Kong, Arushi Goel, Rohan Badlani, Wei Ping, Rafael Valle, and Bryan Catanzaro. Audio flamingo: A novel audio
language model with few-shot learning and dialogue abilities. InInternational Conference on Machine Learning, pages
25125–25148. PMLR, 2024.
Vik Korrapati. Moondream. Online, 2024.
Hugo Laurençon, Lucile Saulnier, Leo Tronchon, Stas Bekman, Amanpreet Singh, Anton Lozhkov, Thomas Wang, Siddharth
Karamcheti, Alexander M Rush, Douwe Kiela, Matthieu Cord, and Victor Sanh. OBELICS: An open web-scale filtered
dataset of interleaved image-text documents. InThirty-Seventh Conference on Neural Information Processing Systems
Datasets and Benchmarks Track, 2023.
71

[PAGE 72]

Hugo Laurençon, Léo Tronchon, Matthieu Cord, and Victor Sanh. What matters when building vision-language models?, May
2024.
Joonho Lee, Jemin Hwangbo, Lorenz Wellhausen, Vladlen Koltun, and Marco Hutter. Learning Quadrupedal Locomotion over
Challenging Terrain.Science Robotics, 5(47):eabc5986, October 2020. ISSN 2470-9476. doi: 10.1126/scirobotics.abc5986.
Seungjae Lee, Yibin Wang, Haritheja Etukuru, H. Jin Kim, Nur Muhammad Mahi Shafiullah, and Lerrel Pinto. Behavior
Generation with Latent Actions, June 2024.
Junnan Li, Dongxu Li, Silvio Savarese, and Steven Hoi. BLIP-2: Bootstrapping language-image pre-training with frozen image
encoders and large language models. InProceedings of the 40th International Conference on Machine Learning, ICML’23, ,
Honolulu, Hawaii, USA„ 2023. JMLR.org.
Timothy P. Lillicrap, Jonathan J. Hunt, Alexander Pritzel, Nicolas Heess, Tom Erez, Yuval Tassa, David Silver, and Daan
Wierstra. Continuous control with deep reinforcement learning, July 2019.
Ji Lin, Hongxu Yin, Wei Ping, Yao Lu, Pavlo Molchanov, Andrew Tao, Huizi Mao, Jan Kautz, Mohammad Shoeybi, and Song
Han. VILA: On Pre-training for Visual Language Models, May 2024.
Yaron Lipman, Ricky T. Q. Chen, Heli Ben-Hamu, Maximilian Nickel, and Matt Le. Flow Matching for Generative Modeling,
February 2023.
Yaron Lipman, Marton Havasi, Peter Holderrieth, Neta Shaul, Matt Le, Brian Karrer, Ricky T. Q. Chen, David Lopez-Paz,
Heli Ben-Hamu, and Itai Gat. Flow Matching Guide and Code, December 2024.
Haotian Liu, Chunyuan Li, Yuheng Li, and Yong Jae Lee. Improved baselines with visual instruction tuning. InNeurIPS 2023
Workshop on Instruction Tuning and Instruction Following, 2023.
Jiajun Liu, Yibing Wang, Hanghang Ma, Xiaoping Wu, Xiaoqi Ma, Xiaoming Wei, Jianbin Jiao, Enhua Wu, and Jie Hu.
Kangaroo: A powerful video-language model supporting long-context video input.arXiv preprint arXiv:2408.15542, 2024.
Calvin Luo. Understanding Diffusion Models: A Unified Perspective, August 2022.
Jianlan Luo, Charles Xu, Jeffrey Wu, and Sergey Levine. Precise and Dexterous Robotic Manipulation via Human-in-the-Loop
Reinforcement Learning, October 2024.
Jianlan Luo, Zheyuan Hu, Charles Xu, You Liang Tan, Jacob Berg, Archit Sharma, Stefan Schaal, Chelsea Finn, Abhishek
Gupta, and Sergey Levine. SERL: A Software Suite for Sample-Efficient Robotic Reinforcement Learning, March 2025.
Kevin M. Lynch and Frank C. Park.Modern Robotics: Mechanics, Planning, and Control. Cambridge University Press, 1
edition, May 2017. ISBN 978-1-316-66123-9 978-1-107-15630-2 978-1-316-60984-2. doi: 10.1017/9781316661239.
Oscar Mañas, Pau Rodriguez Lopez, Saba Ahmadi, Aida Nematzadeh, Yash Goyal, and Aishwarya Agrawal. MAPL:
Parameter-efficient adaptation of unimodal pre-trained models for vision-language few-shot prompting. In Andreas Vlachos
and Isabelle Augenstein, editors,Proceedings of the 17th Conference of the European Chapter of the Association for
Computational Linguistics, pages 2523–2548, Dubrovnik, Croatia, May 2023. Association for Computational Linguistics. doi:
10.18653/v1/2023.eacl-main.185.
Andrés Marafioti, Orr Zohar, Miquel Farré, Merve Noyan, Elie Bakouch, Pedro Cuenca, Cyril Zakka, Loubna Ben Allal, Anton
Lozhkov, Nouamane Tazi, Vaibhav Srivastav, Joshua Lochner, Hugo Larcher, Mathieu Morlon, Lewis Tunstall, Leandro von
Werra, and Thomas Wolf. SmolVLM: Redefining small and efficient multimodal models, April 2025.
Gabriel B. Margolis, Ge Yang, Kartik Paigwar, Tao Chen, and Pulkit Agrawal. Rapid Locomotion via Reinforcement Learning,
May 2022.
John McCormac, Ankur Handa, Andrew Davison, and Stefan Leutenegger. SemanticFusion: Dense 3D Semantic Mapping with
Convolutional Neural Networks, September 2016.
Volodymyr Mnih, Koray Kavukcuoglu, David Silver, Alex Graves, Ioannis Antonoglou, Daan Wierstra, and Martin Riedmiller.
Playing Atari with Deep Reinforcement Learning, December 2013.
Preetum Nakkiran, Arwen Bradley, Hattie Zhou, and Madhu Advani. Step-by-Step Diffusion: An Elementary Tutorial, June
2024.
72

[PAGE 73]

Abby O’Neill, Abdul Rehman, Abhinav Gupta, Abhiram Maddukuri, Abhishek Gupta, Abhishek Padalkar, Abraham Lee,
Acorn Pooley, Agrim Gupta, Ajay Mandlekar, Ajinkya Jain, Albert Tung, Alex Bewley, Alex Herzog, Alex Irpan, Alexander
Khazatsky, Anant Rai, Anchit Gupta, Andrew Wang, Andrey Kolobov, Anikait Singh, Animesh Garg, Aniruddha Kembhavi,
Annie Xie, Anthony Brohan, Antonin Raffin, Archit Sharma, Arefeh Yavary, Arhan Jain, Ashwin Balakrishna, Ayzaan
Wahid, Ben Burgess-Limerick, Beomjoon Kim, Bernhard Schölkopf, Blake Wulfe, Brian Ichter, Cewu Lu, Charles Xu,
Charlotte Le, Chelsea Finn, Chen Wang, Chenfeng Xu, Cheng Chi, Chenguang Huang, Christine Chan, Christopher Agia,
Chuer Pan, Chuyuan Fu, Coline Devin, Danfei Xu, Daniel Morton, Danny Driess, Daphne Chen, Deepak Pathak, Dhruv
Shah, Dieter Büchler, Dinesh Jayaraman, Dmitry Kalashnikov, Dorsa Sadigh, Edward Johns, Ethan Foster, Fangchen Liu,
Federico Ceola, Fei Xia, Feiyu Zhao, Felipe Vieira Frujeri, Freek Stulp, Gaoyue Zhou, Gaurav S. Sukhatme, Gautam Salhotra,
Ge Yan, Gilbert Feng, Giulio Schiavi, Glen Berseth, Gregory Kahn, Guangwen Yang, Guanzhi Wang, Hao Su, Hao-Shu
Fang, Haochen Shi, Henghui Bao, Heni Ben Amor, Henrik I. Christensen, Hiroki Furuta, Homanga Bharadhwaj, Homer
Walke, Hongjie Fang, Huy Ha, Igor Mordatch, Ilija Radosavovic, Isabel Leal, Jacky Liang, Jad Abou-Chakra, Jaehyung Kim,
Jaimyn Drake, Jan Peters, Jan Schneider, Jasmine Hsu, Jay Vakil, Jeannette Bohg, Jeffrey Bingham, Jeffrey Wu, Jensen
Gao, Jiaheng Hu, Jiajun Wu, Jialin Wu, Jiankai Sun, Jianlan Luo, Jiayuan Gu, Jie Tan, Jihoon Oh, Jimmy Wu, Jingpei
Lu, Jingyun Yang, Jitendra Malik, João Silvério, Joey Hejna, Jonathan Booher, Jonathan Tompson, Jonathan Yang, Jordi
Salvador, Joseph J. Lim, Junhyek Han, Kaiyuan Wang, Kanishka Rao, Karl Pertsch, Karol Hausman, Keegan Go, Keerthana
Gopalakrishnan, Ken Goldberg, Kendra Byrne, Kenneth Oslund, Kento Kawaharazuka, Kevin Black, Kevin Lin, Kevin
Zhang, Kiana Ehsani, Kiran Lekkala, Kirsty Ellis, Krishan Rana, Krishnan Srinivasan, Kuan Fang, Kunal Pratap Singh,
Kuo-Hao Zeng, Kyle Hatch, Kyle Hsu, Laurent Itti, Lawrence Yunliang Chen, Lerrel Pinto, Li Fei-Fei, Liam Tan, Linxi "Jim"
Fan, Lionel Ott, Lisa Lee, Luca Weihs, Magnum Chen, Marion Lepert, Marius Memmel, Masayoshi Tomizuka, Masha
Itkina, Mateo Guaman Castro, Max Spero, Maximilian Du, Michael Ahn, Michael C. Yip, Mingtong Zhang, Mingyu Ding,
Minho Heo, Mohan Kumar Srirama, Mohit Sharma, Moo Jin Kim, Muhammad Zubair Irshad, Naoaki Kanazawa, Nicklas
Hansen, Nicolas Heess, Nikhil J. Joshi, Niko Suenderhauf, Ning Liu, Norman Di Palo, Nur Muhammad Mahi Shafiullah,
Oier Mees, Oliver Kroemer, Osbert Bastani, Pannag R. Sanketi, Patrick "Tree" Miller, Patrick Yin, Paul Wohlhart, Peng
Xu, Peter David Fagan, Peter Mitrano, Pierre Sermanet, Pieter Abbeel, Priya Sundaresan, Qiuyu Chen, Quan Vuong, Rafael
Rafailov, Ran Tian, Ria Doshi, Roberto Martín-Martín, Rohan Baijal, Rosario Scalise, Rose Hendrix, Roy Lin, Runjia Qian,
Ruohan Zhang, Russell Mendonca, Rutav Shah, Ryan Hoque, Ryan Julian, Samuel Bustamante, Sean Kirmani, Sergey
Levine, Shan Lin, Sherry Moore, Shikhar Bahl, Shivin Dass, Shubham Sonawani, Shubham Tulsiani, Shuran Song, Sichun
Xu, Siddhant Haldar, Siddharth Karamcheti, Simeon Adebola, Simon Guist, Soroush Nasiriany, Stefan Schaal, Stefan Welker,
Stephen Tian, Subramanian Ramamoorthy, Sudeep Dasari, Suneel Belkhale, Sungjae Park, Suraj Nair, Suvir Mirchandani,
Takayuki Osa, Tanmay Gupta, Tatsuya Harada, Tatsuya Matsushima, Ted Xiao, Thomas Kollar, Tianhe Yu, Tianli Ding,
Todor Davchev, Tony Z. Zhao, Travis Armstrong, Trevor Darrell, Trinity Chung, Vidhi Jain, Vikash Kumar, Vincent
Vanhoucke, Vitor Guizilini, Wei Zhan, Wenxuan Zhou, Wolfram Burgard, Xi Chen, Xiangyu Chen, Xiaolong Wang, Xinghao
Zhu, Xinyang Geng, Xiyuan Liu, Xu Liangwei, Xuanlin Li, Yansong Pang, Yao Lu, Yecheng Jason Ma, Yejin Kim, Yevgen
Chebotar, Yifan Zhou, Yifeng Zhu, Yilin Wu, Ying Xu, Yixuan Wang, Yonatan Bisk, Yongqiang Dou, Yoonyoung Cho,
Youngwoon Lee, Yuchen Cui, Yue Cao, Yueh-Hua Wu, Yujin Tang, Yuke Zhu, Yunchu Zhang, Yunfan Jiang, Yunshuang Li,
Yunzhu Li, Yusuke Iwasawa, Yutaka Matsuo, Zehan Ma, Zhuo Xu, Zichen Jeff Cui, Zichen Zhang, Zipeng Fu, and Zipeng
Lin. Open X-Embodiment: Robotic Learning Datasets and RT-X Models, May 2025.
Maxime Oquab, Timothée Darcet, Théo Moutakanni, Huy Vo, Marc Szafraniec, Vasil Khalidov, Pierre Fernandez, Daniel
Haziza, Francisco Massa, Alaaeldin El-Nouby, Mahmoud Assran, Nicolas Ballas, Wojciech Galuba, Russell Howes, Po-Yao
Huang, Shang-Wen Li, Ishan Misra, Michael Rabbat, Vasu Sharma, Gabriel Synnaeve, Hu Xu, Hervé Jegou, Julien Mairal,
Patrick Labatut, Armand Joulin, and Piotr Bojanowski. DINOv2: Learning Robust Visual Features without Supervision,
February 2024.
Frank Permenter and Chenyang Yuan. Interpreting and Improving Diffusion Models from an Optimization Perspective, June
2024.
Adam Polyak, Amit Zohar, Andrew Brown, Andros Tjandra, Animesh Sinha, Ann Lee, Apoorv Vyas, Bowen Shi, Chih-Yao
Ma, Ching-Yao Chuang, David Yan, Dhruv Choudhary, Dingkang Wang, Geet Sethi, Guan Pang, Haoyu Ma, Ishan Misra,
Ji Hou, Jialiang Wang, Kiran Jagadeesh, Kunpeng Li, Luxin Zhang, Mannat Singh, Mary Williamson, Matt Le, Matthew Yu,
Mitesh Kumar Singh, Peizhao Zhang, Peter Vajda, Quentin Duval, Rohit Girdhar, Roshan Sumbaly, Sai Saketh Rambhatla,
Sam Tsai, Samaneh Azadi, Samyak Datta, Sanyuan Chen, Sean Bell, Sharadh Ramaswamy, Shelly Sheynin, Siddharth
Bhattacharya, Simran Motwani, Tao Xu, Tianhe Li, Tingbo Hou, Wei-Ning Hsu, Xi Yin, Xiaoliang Dai, Yaniv Taigman,
Yaqiao Luo, Yen-Cheng Liu, Yi-Chiao Wu, Yue Zhao, Yuval Kirstain, Zecheng He, Zijian He, Albert Pumarola, Ali Thabet,
Artsiom Sanakoyeu, Arun Mallya, Baishan Guo, Boris Araya, Breena Kerr, Carleigh Wood, Ce Liu, Cen Peng, Dimitry
Vengertsev, Edgar Schonfeld, Elliot Blanchard, Felix Juefei-Xu, Fraylie Nord, Jeff Liang, John Hoffman, Jonas Kohler, Kaolin
Fire, Karthik Sivakumar, Lawrence Chen, Licheng Yu, Luya Gao, Markos Georgopoulos, Rashel Moritz, Sara K. Sampson,
Shikai Li, Simone Parmeggiani, Steve Fine, Tara Fowler, Vladan Petrovic, and Yuming Du. Movie Gen: A Cast of Media
Foundation Models, February 2025.
Dean A. Pomerleau. ALVINN: An Autonomous Land Vehicle in a Neural Network. InAdvances in Neural Information
Processing Systems, volume 1. Morgan-Kaufmann, 1988.
73

[PAGE 74]

Simon J.D. Prince.Understanding Deep Learning. The MIT Press, 2023.
Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell,
Pamela Mishkin, Jack Clark, Gretchen Krueger, and Ilya Sutskever. Learning Transferable Visual Models From Natural
Language Supervision, February 2021.
Colin Raffel, Noam Shazeer, Adam Roberts, Katherine Lee, Sharan Narang, Michael Matena, Yanqi Zhou, Wei Li, and Peter J.
Liu. Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer, September 2023.
Scott Reed, Konrad Zolna, Emilio Parisotto, Sergio Gomez Colmenarejo, Alexander Novikov, Gabriel Barth-Maron, Mai
Gimenez, Yury Sulsky, Jackie Kay, Jost Tobias Springenberg, Tom Eccles, Jake Bruce, Ali Razavi, Ashley Edwards, Nicolas
Heess, Yutian Chen, Raia Hadsell, Oriol Vinyals, Mahyar Bordbar, and Nando de Freitas. A Generalist Agent, November
2022.
Olaf Ronneberger, Philipp Fischer, and Thomas Brox. U-Net: Convolutional Networks for Biomedical Image Segmentation,
May 2015.
Stephane Ross, Geoffrey J. Gordon, and J. Andrew Bagnell. A Reduction of Imitation Learning and Structured Prediction to
No-Regret Online Learning, March 2011.
Lindsay Sanneman, Christopher Fourie, and Julie A. Shah. The State of Industrial Robotics: Emerging Technologies, Challenges,
and Key Research Directions, October 2020.
C Schuhmann, A Köpf, R Vencu, T Coombes, and R Beaumont. Laion coco: 600m synthetic captions from laion2b-en.URL
https://laion.ai/blog/laion-coco, 2022.
John Schulman, Sergey Levine, Philipp Moritz, Michael I. Jordan, and Pieter Abbeel. Trust Region Policy Optimization, April
2017a.
John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Radford, and Oleg Klimov. Proximal Policy Optimization Algorithms,
August 2017b.
Shai Shalev-Shwartz and Shai Ben-David.Understanding Machine Learning: From Theory to Algorithms. Cambridge University
Press, 1 edition, May 2014. ISBN 978-1-107-05713-5 978-1-107-29801-9. doi: 10.1017/CBO9781107298019.
Mustafa Shukor, Corentin Dancette, and Matthieu Cord. Ep-alm: Efficient perceptual augmentation of language models. In
Proceedings of the IEEE/CVF International Conference on Computer Vision, pages 22056–22069, 2023.
Mustafa Shukor, Dana Aubakirova, Francesco Capuano, Pepijn Kooijmans, Steven Palma, Adil Zouitine, Michel Aractingi,
Caroline Pascal, Martino Russi, Andres Marafioti, Simon Alibert, Matthieu Cord, Thomas Wolf, and Remi Cadene. SmolVLA:
A Vision-Language-Action Model for Affordable and Efficient Robotics, June 2025.
Bruno Siciliano and Oussama Khatib, editors.Springer Handbook of Robotics. Springer Handbooks. Springer International
Publishing, Cham, 2016. ISBN 978-3-319-32550-7 978-3-319-32552-1. doi: 10.1007/978-3-319-32552-1.
David Silver, Guy Lever, Nicolas Heess, Thomas Degris, Daan Wierstra, and Martin Riedmiller. Deterministic policy gradient
algorithms. In Eric P. Xing and Tony Jebara, editors,Proceedings of the 31st International Conference on Machine Learning,
volume 32 ofProceedings of Machine Learning Research, pages 387–395, Bejing, China, June 2014. PMLR.
Kihyuk Sohn, Honglak Lee, and Xinchen Yan. Learning Structured Output Representation using Deep Conditional Generative
Models. InAdvances in Neural Information Processing Systems, volume 28. Curran Associates, Inc., 2015.
Jiaming Song, Chenlin Meng, and Stefano Ermon. Denoising Diffusion Implicit Models, October 2022.
Richard S. Sutton and Andrew G. Barto.Reinforcement Learning: An Introduction. Adaptive Computation and Machine
Learning Series. The MIT Press, Cambridge, Massachusetts, second edition edition, 2018. ISBN 978-0-262-03924-6.
Matthew Tancik, Pratul P. Srinivasan, Ben Mildenhall, Sara Fridovich-Keil, Nithin Raghavan, Utkarsh Singhal, Ravi Ra-
mamoorthi, Jonathan T. Barron, and Ren Ng. Fourier Features Let Networks Learn High Frequency Functions in Low
Dimensional Domains, June 2020.
Chen Tang, Ben Abbatematteo, Jiaheng Hu, Rohan Chandra, Roberto Martín-Martín, and Peter Stone. Deep Reinforcement
Learning for Robotics: A Survey of Real-World Successes.Annual Review of Control, Robotics, and Autonomous Systems, 8
(Volume 8, 2025):153–188, May 2025. ISSN 2573-5144. doi: 10.1146/annurev-control-030323-022510.
Yang Tang, Chaoqiang Zhao, Jianrui Wang, Chongzhen Zhang, Qiyu Sun, Weixing Zheng, Wenli Du, Feng Qian, and Juergen
Kurths. Perception and Navigation in Autonomous Systems in the Era of Learning: A Survey.IEEE Transactions on Neural
Networks and Learning Systems, 34(12):9604–9624, December 2023. ISSN 2162-237X, 2162-2388. doi: 10.1109/TNNLS.2022.
3167688.
74

[PAGE 75]

Gemma Team, Morgane Riviere, Shreya Pathak, Pier Giuseppe Sessa, Cassidy Hardin, Surya Bhupatiraju, Léonard Hussenot,
Thomas Mesnard, Bobak Shahriari, Alexandre Ramé, Johan Ferret, Peter Liu, Pouya Tafti, Abe Friesen, Michelle Casbon,
Sabela Ramos, Ravin Kumar, Charline Le Lan, Sammy Jerome, Anton Tsitsulin, Nino Vieillard, Piotr Stanczyk, Sertan
Girgin, Nikola Momchev, Matt Hoffman, Shantanu Thakoor, Jean-Bastien Grill, Behnam Neyshabur, Olivier Bachem,
Alanna Walton, Aliaksei Severyn, Alicia Parrish, Aliya Ahmad, Allen Hutchison, Alvin Abdagic, Amanda Carl, Amy Shen,
Andy Brock, Andy Coenen, Anthony Laforge, Antonia Paterson, Ben Bastian, Bilal Piot, Bo Wu, Brandon Royal, Charlie
Chen, Chintu Kumar, Chris Perry, Chris Welty, Christopher A. Choquette-Choo, Danila Sinopalnikov, David Weinberger,
Dimple Vijaykumar, Dominika Rogozińska, Dustin Herbison, Elisa Bandy, Emma Wang, Eric Noland, Erica Moreira, Evan
Senter, Evgenii Eltyshev, Francesco Visin, Gabriel Rasskin, Gary Wei, Glenn Cameron, Gus Martins, Hadi Hashemi, Hanna
Klimczak-Plucińska, Harleen Batra, Harsh Dhand, Ivan Nardini, Jacinda Mein, Jack Zhou, James Svensson, Jeff Stanway,
Jetha Chan, Jin Peng Zhou, Joana Carrasqueira, Joana Iljazi, Jocelyn Becker, Joe Fernandez, Joost van Amersfoort, Josh
Gordon, Josh Lipschultz, Josh Newlan, Ju-yeong Ji, Kareem Mohamed, Kartikeya Badola, Kat Black, Katie Millican, Keelin
McDonell, Kelvin Nguyen, Kiranbir Sodhia, Kish Greene, Lars Lowe Sjoesund, Lauren Usui, Laurent Sifre, Lena Heuermann,
Leticia Lago, Lilly McNealus, Livio Baldini Soares, Logan Kilpatrick, Lucas Dixon, Luciano Martins, Machel Reid, Manvinder
Singh, Mark Iverson, Martin Görner, Mat Velloso, Mateo Wirth, Matt Davidow, Matt Miller, Matthew Rahtz, Matthew
Watson, Meg Risdal, Mehran Kazemi, Michael Moynihan, Ming Zhang, Minsuk Kahng, Minwoo Park, Mofi Rahman, Mohit
Khatwani, Natalie Dao, Nenshad Bardoliwalla, Nesh Devanathan, Neta Dumai, Nilay Chauhan, Oscar Wahltinez, Pankil
Botarda, Parker Barnes, Paul Barham, Paul Michel, Pengchong Jin, Petko Georgiev, Phil Culliton, Pradeep Kuppala,
Ramona Comanescu, Ramona Merhej, Reena Jana, Reza Ardeshir Rokni, Rishabh Agarwal, Ryan Mullins, Samaneh Saadat,
Sara Mc Carthy, Sarah Perrin, Sébastien M. R. Arnold, Sebastian Krause, Shengyang Dai, Shruti Garg, Shruti Sheth, Sue
Ronstrom, Susan Chan, Timothy Jordan, Ting Yu, Tom Eccles, Tom Hennigan, Tomas Kocisky, Tulsee Doshi, Vihan Jain,
Vikas Yadav, Vilobh Meshram, Vishal Dharmadhikari, Warren Barkley, Wei Wei, Wenming Ye, Woohyun Han, Woosuk
Kwon, Xiang Xu, Zhe Shen, Zhitao Gong, Zichuan Wei, Victor Cotruta, Phoebe Kirk, Anand Rao, Minh Giang, Ludovic
Peran, Tris Warkentin, Eli Collins, Joelle Barral, Zoubin Ghahramani, Raia Hadsell, D. Sculley, Jeanine Banks, Anca Dragan,
Slav Petrov, Oriol Vinyals, Jeff Dean, Demis Hassabis, Koray Kavukcuoglu, Clement Farabet, Elena Buchatskaya, Sebastian
Borgeaud, Noah Fiedel, Armand Joulin, Kathleen Kenealy, Robert Dadashi, and Alek Andreev. Gemma 2: Improving Open
Language Models at a Practical Size, August 2024.
Russ Tedrake. Robotic Manipulation. Perception, Planning and Control., a.
Russ Tedrake. Underactuated Robotics. Algorithms for Walking, Running, Swimming, Flying, and Manipulation, b.
Gabriele Tiboni, Karol Arndt, and Ville Kyrki. DROPO: Sim-to-Real Transfer with Offline Domain Randomization, January
2023.
Gabriele Tiboni, Pascal Klink, Jan Peters, Tatiana Tommasi, Carlo D’Eramo, and Georgia Chalvatzaki. Domain Randomization
via Entropy Maximization, March 2024.
Josh Tobin, Rachel Fong, Alex Ray, Jonas Schneider, Wojciech Zaremba, and Pieter Abbeel. Domain Randomization for
Transferring Deep Neural Networks from Simulation to the Real World, March 2017.
Peter Tong, Ellis Brown, Penghao Wu, Sanghyun Woo, Adithya Jairam Vedagiri IYER, Sai Charitha Akula, Shusheng Yang,
Jihan Yang, Manoj Middepogu, Ziteng Wang, et al. Cambrian-1: A fully open, vision-centric exploration of multimodal llms.
Advances in Neural Information Processing Systems, 37:87310–87356, 2024.
Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine Babaei, Nikolay Bashlykov, Soumya Batra,
Prajjwal Bhargava, Shruti Bhosale, Dan Bikel, Lukas Blecher, Cristian Canton Ferrer, Moya Chen, Guillem Cucurull, David
Esiobu, Jude Fernandes, Jeremy Fu, Wenyin Fu, Brian Fuller, Cynthia Gao, Vedanuj Goswami, Naman Goyal, Anthony
Hartshorn, Saghar Hosseini, Rui Hou, Hakan Inan, Marcin Kardas, Viktor Kerkez, Madian Khabsa, Isabel Kloumann, Artem
Korenev, Punit Singh Koura, Marie-Anne Lachaux, Thibaut Lavril, Jenya Lee, Diana Liskovich, Yinghai Lu, Yuning Mao,
Xavier Martinet, Todor Mihaylov, Pushkar Mishra, Igor Molybog, Yixin Nie, Andrew Poulton, Jeremy Reizenstein, Rashi
Rungta, Kalyan Saladi, Alan Schelten, Ruan Silva, Eric Michael Smith, Ranjan Subramanian, Xiaoqing Ellen Tan, Binh
Tang, Ross Taylor, Adina Williams, Jian Xiang Kuan, Puxin Xu, Zheng Yan, Iliyan Zarov, Yuchen Zhang, Angela Fan,
Melanie Kambadur, Sharan Narang, Aurelien Rodriguez, Robert Stojnic, Sergey Edunov, and Thomas Scialom. Llama 2:
Open Foundation and Fine-Tuned Chat Models, July 2023.
Maria Tsimpoukelli, Jacob L Menick, Serkan Cabi, SM Eslami, Oriol Vinyals, and Felix Hill. Multimodal few-shot learning
with frozen language models.Advances in Neural Information Processing Systems, 34:200–212, 2021.
Théophane Vallaeys, Mustafa Shukor, Matthieu Cord, and Jakob Verbeek. Improved baselines for data-efficient perceptual
augmentation of llms.arXiv preprint arXiv:2403.13499, 2024.
Yi Wang, Xinhao Li, Ziang Yan, Yinan He, Jiashuo Yu, Xiangyu Zeng, Chenting Wang, Changlian Ma, Haian Huang, Jianfei
Gao, et al. InternVideo2. 5: Empowering video mllms with long and rich context modeling.arXiv preprint arXiv:2501.12386,
2025.
75

[PAGE 76]

Yuan Yao, Tianyu Yu, Ao Zhang, Chongyi Wang, Junbo Cui, Hongji Zhu, Tianchi Cai, Haoyu Li, Weilin Zhao, Zhihui He,
Qianyu Chen, Huarong Zhou, Zhensheng Zou, Haoye Zhang, Shengding Hu, Zhi Zheng, Jie Zhou, Jie Cai, Xu Han, Guoyang
Zeng, Dahai Li, Zhiyuan Liu, and Maosong Sun. MiniCPM-v: A GPT-4V level MLLM on your phone, 2024.
Xiaohua Zhai, Basil Mustafa, Alexander Kolesnikov, and Lucas Beyer. Sigmoid Loss for Language Image Pre-Training,
September 2023.
Boqiang Zhang, Kehan Li, Zesen Cheng, Zhiqiang Hu, Yuqian Yuan, Guanzheng Chen, Sicong Leng, Yuming Jiang, Hang
Zhang, Xin Li, et al. VideoLLaMA 3: Frontier multimodal foundation models for image and video understanding.arXiv
preprint arXiv:2501.13106, 2025.
Chong Zhang, Wenli Xiao, Tairan He, and Guanya Shi. WoCoCo: Learning Whole-Body Humanoid Control with Sequential
Contacts, November 2024.
Tony Z. Zhao, Vikash Kumar, Sergey Levine, and Chelsea Finn. Learning Fine-Grained Bimanual Manipulation with Low-Cost
Hardware, April 2023.
Deyao Zhu, Jun Chen, Xiaoqian Shen, Xiang Li, and Mohamed Elhoseiny. MiniGPT-4: Enhancing vision-language understanding
with advanced large language models. InThe Twelfth International Conference on Learning Representations, 2024.
Wanrong Zhu, Jack Hessel, Anas Awadalla, Samir Yitzhak Gadre, Jesse Dodge, Alex Fang, Youngjae Yu, Ludwig Schmidt,
William Yang Wang, and Yejin Choi. Multimodal C4: An open, billion-scale corpus of images interleaved with text. In
Thirty-Seventh Conference on Neural Information Processing Systems Datasets and Benchmarks Track, 2023.
76
