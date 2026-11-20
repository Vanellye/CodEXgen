#ifndef PANTHEON_FACULTY_ENGINE_HPP
#define PANTHEON_FACULTY_ENGINE_HPP

#include "pantheon/runtime.hpp"
#include <string>
#include <vector>

namespace pantheon {

struct PerceptionResult {
    NumericMap featureScores;
    std::string strongestFeature;
    double confidence;
    double uncertainty;
    std::size_t evidenceCount;
    PerceptionResult() : featureScores(), strongestFeature(), confidence(0.0),
                         uncertainty(1.0), evidenceCount(0) {}
};

struct CreativeResult {
    std::vector<std::string> concepts;
    std::vector<std::string> combinations;
    std::string seedDigest;
    std::string note;
};

struct AdaptationResult {
    double prediction;
    double observation;
    double priorError;
    double correctedPrediction;
    double posteriorError;
    double gain;
};

struct ChannelInput {
    std::string name;
    double carrierHz;
    double priority;
    std::string mode;
    ChannelInput() : name(), carrierHz(0.0), priority(1.0), mode("digital") {}
};

struct ChannelPlan {
    std::string channel;
    double carrierHz;
    double phaseDegrees;
    double priority;
    std::string mode;
};

class FacultyEngine {
public:
    static PerceptionResult assessPerception(const NumericMap& observations,
                                             const NumericMap& weights = NumericMap());
    static CreativeResult generateIdeas(const std::vector<std::string>& concepts,
                                        int maxCombinations = 12);
    static AdaptationResult adaptPrediction(double prediction, double observation,
                                            double gain = 0.25);
    static std::vector<ChannelPlan> coordinateChannels(
        const std::vector<ChannelInput>& channels);
};

class FacultyModule : public Module {
public:
    std::string name() const;
    Result execute(const Input& input) const;
};

} // namespace pantheon

#endif
