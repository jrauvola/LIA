import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models

def eval_input(interview_instance):
    # dummy interview transcript that needs to be evaluated
    # only for demonstration purposes
    # incoming = """input: \"INTERVIEWER: So how you doing? INTERVIEWEE: Great how about you? INTERVIEWER: I\'m okay. INTERVIEWEE: I\'m a little [???] by the resurgence of the hurricane but..|[laughter] INTERVIEWER: I understand I got to get home later too and I\'m worried. INTERVIEWEE: Yeah we were half way here and it just turned on a switch lightening winds and everything. INTERVIEWER: Oh wow. INTERVIEWEE: So yeah. INTERVIEWER: So uh tell me about yourself. INTERVIEWEE: Okay um I\'m a Junior here at MIT um I\'m studying aerospace engineering um my my interests are generally in food mechanics control um design um mostly aircraft but protozoan [???] problems in general. Um I like to um I like to play music listen to music um I run do some other team sports I like to play hockey.  INTERVIEWER: Tell me about a time when you demonstrated leadership. INTERVIEWEE: Um okay so uh one of the projects that I\'ve worked on since coming to MIT um was during my Freshman year I worked in the in the uh Artificial Intelligence group in uh Cesil [sp] which is a lab a computer science lab here at MIT. INTERVIEWER: Okay. INTERVIEWEE: And um I was working on a project with another student actually another Freshman uh basically we were tasked with the sort of bringing this project starting this project bring it up to the level where it could be presented at conference.  INTERVIEWER: Mm-hmm. INTERVIEWEE: Um together and we were kind of left to work out the cooperation on our own and um  there was um as the conference got closer about halfway um about halfway through the year Freshman year ah there were a bunch of issues that we had with um with um basically meeting the expectations that had been set before us in terms of what we were going to present. Um and finishing in a timely basis. INTERVIEWER: Mm-hmm. INTERVIEWEE: And it came down to whether we were really going to be able to and there were other basically parts other people\'s work in the same group where work depended on us finishing in time so it really um really we had to make a decision weather we were just going to basically get done what we could but to the quality standard that the standard of quality that was expected of us or to um try to finish everything and to have other people\'s work potentially suffer because of our [??] hadn\'t really been up to snuff. And um and so we kind of had a little bit of a disagreement about this but what ended up happening was um I went and talked to the professor and um sort of decided to um make them aware of what was happening because they weren\'t really aware that we had fallen behind. And um sort of got the other student on board who had disagreed with me uh to do this uh and to let everyone else know what was going on and uh we ended up presenting a lot less than what was originally expected but um I think it was very much for the better.  INTERVIEWER: Tell me about a time when you were working on a team and you were faced with a challenge. How did you solve the problem? INTERVIEWEE: Okay um so another another thing that I spend a lot of my time doing is called is an organization called Design Build Fly here um it\'s it\'s a design competition um run by the IAA which is an aerospace professional organization. And um  and uh you can enter a team from any university or group basically anywhere in the world. It\'s mostly US university though. INTERVIEWER: Mm-hmm. INTERVIEWEE: And um these university teams basically build a plane um design it build it fly it as the competition name suggests and you compete them all at the end of the year compete against the other universities at the end of the year at one competition. Basically um last year we had uh a design challenge it was pretty unique um and um so I\'ll take that as our challenge um so we basically had a year to solve this um and I was head of one of the sub-groups last year the actual design sub-group and um I mean we approached in a methodical way just like I think that\'s the best way to solve most problems.  INTERVIEWER: Sure. INTERVIEWEE: Um got input from every team member um and um basically um looked at looked at all our possibilities um  and um we ran the numbers. Ultimately like I think that\'s the best way to solve most problems. We ended up with um a design that got the best overall score... INTERVIEWER: Mm-hmm. INTERVIEWEE: ...on the basis of just basically incorporating um every team member\'s input. INTERVIEWER: Mm-hmm. Tell me about one of your weaknesses and how you plan to overcome it. INTERVIEWEE: Okay um so one of my I think definitely since coming here I\'ve noticed that one of my biggest weaknesses is written communication. Um I really was not intimidated by the thought of it in high school but I um definitely since coming here I find that perhaps um at the expense of technical skills my written communication skills have atrophied maybe is the right word. And um so I definitely I think I\'m um pretty aware of this and um and um.. I would definitely like to improve it and um... INTERVIEWER: Mm-hmm. INTERVIEWEE: ...so what I\'m going to do is try to force myself whenever I\'m writing papers or taking reports for whether it be for research or for classes just to go through the proper revision cycle force myself to make sure that I\'m actually being um that I\'m being succinct in what I\'m saying have other people reading give me feedback. INTERVIEWER: Now why do you think that we should hire you for this position? INTERVIEWEE: Okay um I um I mean I think I don\'t know what this position that it is... INTERVIEWER: Whatever position you want at a company that you\'re looking for. INTERVIEWEE: Yeah sure but if I knew that this position was I think that I would want it because um this is really what I thrive off of. I um enjoy doing it um and I would be excited to come to work every day to do it. Um which um that\'s like the biggest thing for me. I um I would be excited to come do it and I know I would put my you know put my all into doing a good job at it because I would be excited to come do it. And um I think that um I have a decent skill set to do this and I think that I\'m qualified to contribute in this area. INTERVIEWER: Mm-hmm. Well thank you.\"
    # output:
    # """

    # should be implementing the below for final integrated version of the app

    transcript = f"""You are an interview coach with 10-year experience. Read the following data science interview transcripts between an interviewer and an interviewee. 
        Evaluate the interviewee's answers and give an overall evaluation based on the 
        provide scores and feedback for \'Overall\', \'RecommendHiring\', \'Colleague\', \'Engaged\', \'Excited\', \'NoFillers\', \'Friendly\', \'Paused\', \'StructuredAnswers\', \'Calm\', \'Focused\', \'Authentic\', \'NotAwkward\', \'Total\'. 
        Speak to the interviewee as you are in an interview coaching session. You will only return the prompt in the following format:
        {
    "Overall": [
            {"score": "insert your score rounded to 1 decimal point"}, 
            {"feedback": "insert a 2 line feedback justifying the relevant score"}
        ],
        "RecommendHiring": [
            {"score": "insert your score rounded to 1 decimal point"}, 
            {"feedback": "insert a 1 line feedback justifying the relevant score"}
        ],
        "Colleague": [
            {"score": "insert your score rounded to 1 decimal point"}, 
            {"feedback": "insert a 1 line feedback justifying the relevant score"}
        ],
        "Engaged": [
            {"score": "insert your score rounded to 1 decimal point"}, 
            {"feedback": "insert a 1 line feedback justifying the relevant score"}
        ],
        "Excited": [
            {"score": "insert your score rounded to 1 decimal point"}, 
            {"feedback": "insert a 1 line feedback justifying the relevant score"}
        ],
        "NoFillers": [
            {"score": "insert your score rounded to 1 decimal point"}, 
            {"feedback": "insert a 1 line feedback justifying the relevant score"}
        ],
        "Friendly": [
            {"score": "insert your score rounded to 1 decimal point"}, 
            {"feedback": "insert a 1 line feedback justifying the relevant score"}
        ],
        "Paused": [
            {"score": "insert your score rounded to 1 decimal point"}, 
            {"feedback": "insert a 1 line feedback justifying the relevant score"}
        ],
        "StructuredAnswers": [
            {"score": "insert your score rounded to 1 decimal point"}, 
            {"feedback": "insert a 1 line feedback justifying the relevant score"}
        ],
        "Calm": [
            {"score": "insert your score rounded to 1 decimal point"}, 
            {"feedback": "insert a 1 line feedback justifying the relevant score"}
        ],
        "Focused": [
            {"score": "insert your score rounded to 1 decimal point"}, 
            {"feedback": "insert a 1 line feedback justifying the relevant score"}
        ],
        "Authentic": [
            {"score": "insert your score rounded to 1 decimal point"}, 
            {"feedback": "insert a 1 line feedback justifying the relevant score"}
        ],
        "NotAwkward": [
            {"score": "insert your score rounded to 1 decimal point"}, 
            {"feedback": "insert a 1 line feedback justifying the relevant score"}
        ],
        "Total": [
            {"score": "insert your score rounded to 1 decimal point"}, 
            {"feedback": "insert a 1 line feedback justifying the relevant score"}
        ]}

        input: \"INTERVIEWER: So how are you doing? INTERVIEWEE: Im pretty good. INTERVIEWER: Ok well so please tell me about yourself. INTERVIEWEE: ok uhm so have you looked at my resume or should I alright so I guess ah I am course 6-7 here at M.I.T ah which is computational biology so its a mix of computers science and biology and actually thats where my interest lie in applying like algorithmic kinda software engineering too datasets dealing with genomics and biology. Uhm some of that activities that you do out side of school include Camp Kesem which is a summer camp that we run for completely free for kids whose parents have cancer as well as ah amphibious achievement which is ah a high school tutoring program for inner city kids in Boston INTERVIEWER: mhhmm INTERVIEWEE: So ah my interest kinda laid both in a little bit of the health care I imagined I was going be a Doctor growing up and then it came down to the tee and Im like well I can do engineering and still apply and do the same things and help a lot more people. INTERVIEWER: So please tell me about a time that you demonstrated leadership. INTERVIEWEE: Ok uhm one of the things we have to do for Camp Kesem is orgin or fundraise all the money to ah to run the camp which is over $50,000.00. Ah so one of the things that I individually spearhead every year is called the Camp Kesem I say you did auction where actually my fraternity and I go out and solicit uhm donations in the form of gift cards ah to raise money for a date auction where we actually sell dates and then we use this money obviously we donate it to Camp Kesem. I spearhead the entire event and I kinda orginize everyone into committees and groups and I send the people out and make sure everything goes according to plan. INTERVIEWER: Tell me about a time when your working on a team and faced with a challenge how did you solve that problem? INTERVIEWEE: Ahh I guess the easiest team project I just I just had was last semester uhm I worked on this six double o five project which is algorithm or software architecture. INTERVIEWER: uh hun. INTERVIEWEE: and we were put in a group of 3 people and it was standard you know we signed the contract everyone is supposed to work equally but it ended up being by the end of it that someone didn\'t like put there fair share of work in...Ah essentially we talked to him we didn\'t really get it out we actually had to go to some of the T.A\'s we got a little bit ah and that kinda like pushed him forward so I mean I guess what I am showing is like Im not affraid to go to the right method or like authority like where in cases this situation presents itself. INTERVIEWER: Oh yes. Alright tell me about one of your weaknesses and how you plan to overcome it. INTERVIEWEE: Uhmmm. I would say for this job ah Im a little technically underprepared. Ah I\'ve yet I have only taken the introductory software classes so far and as well as introductory bio classes but I think just from sheer interest and sheer effort i will be able to kinda overcome these obstacles. INTERVIEWER: Now why do you think we should hire you? INTERVIEWEE: Ah Im very interested in the subject of computation biology and I think that I will be able to contribute a lot to this field uhm I\'ve had a good amount of experience and I think I will be a solid intern. INTERVIEWER: Well thank you.\"
        output: \"Overall: 5.3, RecommendHiring: 5.1, Colleague: 5.3, Engaged: 5.5, Excited: 5.0, NoFillers: 3.8, Friendly: 5.3, Paused: 5.8, StructuredAnswers: 4.9, Calm: 5.4, Focused: 5.8, Authentic: 5.6, NotAwkward: 5.5, Total: 93.1\"

        input: \"INTERVIEWER: So tell me about yourself.  INTERVIEWEE: Uhh I\'m a junior at MIT uhh I\'m double majoring in Management and Biology er I\'m very interested in the world of finance uh business consulting all of those sorts of things. Um so I\'ve tried to take on different leadership roles that would prepare me for uh those sort of roles in the business world. Outside of school I enjoy running cross-country and track I\'m on the varsity team at MIT. And umm I\'m also very involved in Greek Life at MIT so I\'m on the Panhellenic Executive Board as Vice President of Programming and also hold a leadership position in my sorority.  INTERVIEWER: Great okay. Can you tell me about a time you demonstrated leadership? INTERVIEWEE: Umm so I think this past year my biggest priority has been my position as Vice President of Programming for Panhellenic and umm just in that position uhh I hold a leadership role on the exec board. We have weekly meetings I\'m charge of putting together our programming calendar for our entire year. So I have interface with a lot of MIT faculty and bring together the exec board as a whole and the different sororities uhh to meet and attend different events. And I think to put together all these events I\'m working together with different people on campus I have to show leadership and show strong communication skills.  INTERVIEWER: Great. So tell me about a time you were working on a team and faced a challenge. How did you guys overcome that? INTERVIEWEE: Umm so I guess this past semester actually I\'m associate advisor for umm freshmen and I work with my freshmen advisor as well and another associate advisor and er  the three of us were trying to come up with an event to host for the freshman and I think we all er were very uhh set on our ideas. So having to full time communicate and work on an idea that could bring all our thoughts and goals together . Um so we had to work together to formulate some sort of event that would satisfy each of our different goals and that was difficult at first \'cause we had just met each other and it was difficult to understand where the other people were coming from. But after that and after communicating what our main goals for the event for would be we eventually figured out what we wanted to do.  INTERVIEWER: Can you be more specific about that what you eventually figured out? INTERVIEWEE: Uhh yeah so we had - we were trying to communicate via email at first so I think that was uhh inefficient especially since we had only met in a group once before umm so meeting in person and really trying to outline not just like  what the event was going to be what our purpose of the event was going to be and what we trying to communicate with the freshmen. I think by boiling down to what our purpose was for the event we were able to build it up from there.  INTERVIEWER: Okay so can tell me about some of your weakness? Do you have any idea?  INTERVIEWEE: Umm so I think one of my weaknesses is public speaking actually and uhh I think by taking a variety of classes especially this one class that I\'m in that focuses on management and communication . I\'ve been kind of thrown into positions where I have to give impromptu speeches uhh and debate my point in different arguments and I think that the practice is helping me a lot and it allows me to become more comfortable and more confident in what I\'m saying which I think helps me in the long run like public speaking in general. I think I\'ve been able to build up my confidence and know like how to structure my speeches and interviews and impromptus better.  INTERVIEWER: Great. So why do you think we should hire you? INTERVIEWEE: Uhh I think my different leadership positions as well as my academic experience umm would allow me to perform well on the job. I think I\'ve worked umm both individually in a project as well as in a team-focused environment which umm I think is key for consulting and investment banking positions. I also feel that my MIT background uh the quantitative analysis that I\'ve done in classes as well as my internship experiences would help perform well on the job as well so... INTERVIEWER: Great.\"
        output: \"Overall: 4.5, RecommendHiring: 4.5, Colleague: 4.5, Engaged: 5.5, Excited: 4.3, NoFillers: 3.1, Friendly: 5.4, Paused: 5.2, StructuredAnswers: 4.7, Calm: 5.1, Focused: 5.3, Authentic: 5.7, NotAwkward: 4.5, Total: 85.5\"

        input: \"INTERVIEWER: {interview_instance.interview_dict[0]['question']} INTERVIEWEE: {interview_instance.interview_dict[0]['answer']} INTERVIEWER: {interview_instance.interview_dict[1]['question']}INTERVIEWEE: {interview_instance.interview_dict[1]['answer']} INTERVIEWER: {interview_instance.interview_dict[2]['question']} INTERVIEWEE: {interview_instance.interview_dict[2]['answer']} INTERVIEWER: {interview_instance.interview_dict[3]['question']} INTERVIEWEE: {interview_instance.interview_dict[3]['answer']} INTERVIEWER: {interview_instance.interview_dict[4]['question']} INTERVIEWEE: {interview_instance.interview_dict[4]['answer']}\"
        output:
        """

    return transcript

def generate(interview_instance):
  vertexai.init(project="adsp-capstone-team-dawn", location="us-central1")
  transcript = eval_input(interview_instance)
  model = GenerativeModel(
    "gemini-1.5-flash-preview-0514",
  )
  responses = model.generate_content(
      transcript,
      generation_config=generation_config,
      safety_settings=safety_settings,
  )

  return responses.text


generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0.7,
    "top_p": 0.98,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}



'''


instance that needs to be used: interview_instance from main.py
its global
and attribute 'answer' contains transcript
interview_instance.interview_dict[i]['answer']

modify this transcript into the following format:

"""input: \"INTERVIEWER: question1 INTERVIEWEE: answer1 INTERVIEWER: question2 INTERVIEWEE: answer2 INTERVIEWER: question3 INTERVIEWEE: answer3 INTERVIEWER: question4 INTERVIEWEE: answer4 INTERVIEWER: question5 INTERVIEWEE: answer5\"
output:
"""


'''