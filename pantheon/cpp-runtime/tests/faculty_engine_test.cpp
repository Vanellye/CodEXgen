#include "pantheon/faculty_engine.hpp"
#include <cassert>
#include <cmath>
#include <stdexcept>
#include <vector>

int main() {
    pantheon::NumericMap observations;
    observations["signal"]=3.0;
    observations["noise"]=2.0;
    pantheon::NumericMap weights;
    weights["signal"]=2.0;
    pantheon::PerceptionResult perception= pantheon::FacultyEngine::assessPerception(observations,weights);
    assert(perception.strongestFeature=="signal");
    assert(std::fabs(perception.confidence-0.75)<1e-12);
    assert(perception.evidenceCount==2);

    std::vector<std::string> concepts;
    concepts.push_back("light"); concepts.push_back("water"); concepts.push_back("sound");
    pantheon::CreativeResult ideas=pantheon::FacultyEngine::generateIdeas(concepts,2);
    pantheon::CreativeResult ideasAgain=pantheon::FacultyEngine::generateIdeas(concepts,2);
    assert(ideas.combinations.size()==2);
    assert(ideas.seedDigest==ideasAgain.seedDigest);
    assert(ideas.seedDigest=="e616de59affb49d57164af8528ce08b6255b840006c55ccb4f6b20f5905667f4");

    pantheon::AdaptationResult adapted=pantheon::FacultyEngine::adaptPrediction(10.0,14.0,0.5);
    assert(adapted.correctedPrediction==12.0);
    assert(adapted.posteriorError<adapted.priorError);

    std::vector<pantheon::ChannelInput> channels(2);
    channels[0].name="perception"; channels[0].carrierHz=11.0;
    channels[1].name="creativity"; channels[1].carrierHz=1111.0;
    std::vector<pantheon::ChannelPlan> plan=pantheon::FacultyEngine::coordinateChannels(channels);
    assert(plan[0].phaseDegrees==0.0 && plan[1].phaseDegrees==180.0);

    pantheon::Runtime runtime;
    assert(runtime.registerModule(std::shared_ptr<pantheon::Module>(new pantheon::FacultyModule())));
    pantheon::Input input; input.values=observations;
    pantheon::Result moduleResult=runtime.execute("stride.faculty",input);
    assert(moduleResult.ok && moduleResult.message=="signal");

    bool rejected=false;
    try { pantheon::FacultyEngine::adaptPrediction(1.0,2.0,1.5); }
    catch (const std::invalid_argument&) { rejected=true; }
    assert(rejected);
    pantheon::NumericMap empty;
    rejected=false;
    try { pantheon::FacultyEngine::assessPerception(empty); }
    catch (const std::invalid_argument&) { rejected=true; }
    assert(rejected);
    return 0;
}
