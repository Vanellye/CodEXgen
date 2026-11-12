#include "pantheon/faculty_engine.hpp"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <set>
#include <sstream>
#include <stdexcept>

namespace pantheon {
namespace {

double checked(const char* name, double value, double low, double high) {
    if (!std::isfinite(value) || value < low || value > high) {
        std::ostringstream message;
        message << name << " must be finite and within [" << low << ", " << high << "]";
        throw std::invalid_argument(message.str());
    }
    return value;
}

std::string trim(const std::string& value) {
    const std::string::size_type first = value.find_first_not_of(" \t\r\n");
    if (first == std::string::npos) return std::string();
    const std::string::size_type last = value.find_last_not_of(" \t\r\n");
    return value.substr(first, last - first + 1);
}

std::string jsonString(const std::string& value) {
    std::ostringstream out;
    out << '"';
    for (std::string::const_iterator it = value.begin(); it != value.end(); ++it) {
        const unsigned char c = static_cast<unsigned char>(*it);
        if (c == '"' || c == '\\') out << '\\' << static_cast<char>(c);
        else if (c == '\b') out << "\\b";
        else if (c == '\f') out << "\\f";
        else if (c == '\n') out << "\\n";
        else if (c == '\r') out << "\\r";
        else if (c == '\t') out << "\\t";
        else if (c < 0x20) {
            out << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                << static_cast<unsigned int>(c) << std::dec;
        } else out << static_cast<char>(c);
    }
    out << '"';
    return out.str();
}

const std::uint32_t K[64] = {
  0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
  0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
  0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
  0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
  0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
  0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
  0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
  0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
};
std::uint32_t rotr(std::uint32_t x, unsigned n) { return (x >> n) | (x << (32 - n)); }

std::string sha256(const std::string& input) {
    std::vector<unsigned char> data(input.begin(), input.end());
    const std::uint64_t bitLength = static_cast<std::uint64_t>(data.size()) * 8;
    data.push_back(0x80);
    while ((data.size() % 64) != 56) data.push_back(0);
    for (int i = 7; i >= 0; --i) data.push_back(static_cast<unsigned char>(bitLength >> (i * 8)));
    std::uint32_t h[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
                          0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
    for (std::size_t offset = 0; offset < data.size(); offset += 64) {
        std::uint32_t w[64];
        for (int i = 0; i < 16; ++i) {
            const std::size_t p = offset + static_cast<std::size_t>(i) * 4;
            w[i] = (static_cast<std::uint32_t>(data[p]) << 24) |
                   (static_cast<std::uint32_t>(data[p+1]) << 16) |
                   (static_cast<std::uint32_t>(data[p+2]) << 8) | data[p+3];
        }
        for (int i = 16; i < 64; ++i) {
            const std::uint32_t s0 = rotr(w[i-15],7) ^ rotr(w[i-15],18) ^ (w[i-15] >> 3);
            const std::uint32_t s1 = rotr(w[i-2],17) ^ rotr(w[i-2],19) ^ (w[i-2] >> 10);
            w[i] = w[i-16] + s0 + w[i-7] + s1;
        }
        std::uint32_t a=h[0],b=h[1],c=h[2],d=h[3],e=h[4],f=h[5],g=h[6],hh=h[7];
        for (int i = 0; i < 64; ++i) {
            const std::uint32_t s1=rotr(e,6)^rotr(e,11)^rotr(e,25);
            const std::uint32_t ch=(e&f)^(~e&g);
            const std::uint32_t t1=hh+s1+ch+K[i]+w[i];
            const std::uint32_t s0=rotr(a,2)^rotr(a,13)^rotr(a,22);
            const std::uint32_t maj=(a&b)^(a&c)^(b&c);
            const std::uint32_t t2=s0+maj;
            hh=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
        }
        h[0]+=a;h[1]+=b;h[2]+=c;h[3]+=d;h[4]+=e;h[5]+=f;h[6]+=g;h[7]+=hh;
    }
    std::ostringstream out;
    out << std::hex << std::setfill('0');
    for (int i=0;i<8;++i) out << std::setw(8) << h[i];
    return out.str();
}

} // namespace

PerceptionResult FacultyEngine::assessPerception(const NumericMap& observations,
                                                  const NumericMap& weights) {
    if (observations.empty()) throw std::invalid_argument("observations must be non-empty");
    if (observations.size() > 128) throw std::invalid_argument("at most 128 features are supported");
    PerceptionResult result;
    double total = 0.0, peak = 0.0;
    for (NumericMap::const_iterator it=observations.begin(); it!=observations.end(); ++it) {
        if (it->first.empty() || it->first.size()>80)
            throw std::invalid_argument("feature names must be non-empty and at most 80 chars");
        const double value=checked("observation",it->second,-1000000.0,1000000.0);
        NumericMap::const_iterator wi=weights.find(it->first);
        const double weight=checked("weight",wi==weights.end()?1.0:wi->second,0.0,10.0);
        const double score=std::fabs(value)*weight;
        result.featureScores[it->first]=score;
        total+=score;
        if (score>peak) { peak=score; result.strongestFeature=it->first; }
    }
    result.evidenceCount=result.featureScores.size();
    result.confidence=total==0.0?0.0:peak/total;
    result.uncertainty=1.0-result.confidence;
    return result;
}

CreativeResult FacultyEngine::generateIdeas(const std::vector<std::string>& concepts,
                                             int maxCombinations) {
    if (maxCombinations<1 || maxCombinations>64)
        throw std::invalid_argument("max_combinations must be from 1 to 64");
    CreativeResult result;
    std::set<std::string> seen;
    for (std::vector<std::string>::const_iterator it=concepts.begin();it!=concepts.end();++it) {
        const std::string clean=trim(*it);
        if (!clean.empty() && seen.insert(clean).second) result.concepts.push_back(clean);
    }
    if (result.concepts.size()<2 || result.concepts.size()>32)
        throw std::invalid_argument("provide 2 to 32 non-empty concepts");
    std::ostringstream payload;
    payload << '[';
    for (std::size_t i=0;i<result.concepts.size();++i) {
        if (i) payload << ',';
        payload << jsonString(result.concepts[i]);
    }
    payload << ']';
    result.seedDigest=sha256(payload.str());
    for (std::size_t i=0;i<result.concepts.size() && result.combinations.size()<static_cast<std::size_t>(maxCombinations);++i) {
        for (std::size_t j=i+1;j<result.concepts.size() && result.combinations.size()<static_cast<std::size_t>(maxCombinations);++j) {
            result.combinations.push_back("Explore how "+result.concepts[i]+" could inform "+result.concepts[j]);
        }
    }
    result.note="Idea prompts are synthetic suggestions requiring human review.";
    return result;
}

AdaptationResult FacultyEngine::adaptPrediction(double prediction,double observation,double gain) {
    const double p=checked("prediction",prediction,-1000000.0,1000000.0);
    const double o=checked("observation",observation,-1000000.0,1000000.0);
    const double k=checked("gain",gain,0.0,1.0);
    const double error=o-p;
    AdaptationResult r;
    r.prediction=p; r.observation=o; r.priorError=std::fabs(error);
    r.correctedPrediction=p+k*error; r.posteriorError=std::fabs(o-r.correctedPrediction); r.gain=k;
    return r;
}

std::vector<ChannelPlan> FacultyEngine::coordinateChannels(const std::vector<ChannelInput>& channels) {
    if (channels.empty() || channels.size()>16)
        throw std::invalid_argument("provide 1 to 16 channels");
    std::set<std::string> names;
    std::vector<ChannelPlan> result;
    for (std::size_t i=0;i<channels.size();++i) {
        const ChannelInput& item=channels[i];
        if (item.name.empty() || !names.insert(item.name).second)
            throw std::invalid_argument("channel names must be unique and non-empty");
        const double hz=checked("carrier_hz",item.carrierHz,0.1,1111.0);
        const double priority=checked("priority",item.priority,0.0,1.0);
        if (item.mode!="digital" && item.mode!="optical_model" &&
            item.mode!="acoustic_model" && item.mode!="sensor_input")
            throw std::invalid_argument("unsupported channel mode");
        ChannelPlan plan;
        plan.channel=item.name; plan.carrierHz=hz;
        plan.phaseDegrees=static_cast<double>(i)*360.0/static_cast<double>(channels.size());
        plan.priority=priority; plan.mode=item.mode;
        result.push_back(plan);
    }
    return result;
}

std::string FacultyModule::name() const { return "stride.faculty"; }

Result FacultyModule::execute(const Input& input) const {
    Result result;
    result.module=name();
    try {
        const PerceptionResult perception=FacultyEngine::assessPerception(input.values);
        result.ok=true;
        result.message=perception.strongestFeature;
        result.metrics=perception.featureScores;
        result.metrics["confidence"]=perception.confidence;
        result.metrics["uncertainty"]=perception.uncertainty;
        result.metrics["evidence_count"]=static_cast<double>(perception.evidenceCount);
    } catch (const std::exception& error) {
        result.ok=false;
        result.message=error.what();
    }
    return result;
}

} // namespace pantheon
