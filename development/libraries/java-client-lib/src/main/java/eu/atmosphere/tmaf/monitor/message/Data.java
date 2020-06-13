/**
 * <b>ATMOSPHERE</b> - http://www.atmosphere-eubrazil.eu/
 * ***
 * <p>
 * <b>Trustworthiness Monitoring & Assessment Framework</b>
 * Component: Monitor - Client
 * <p>
 * Repository: https://github.com/eubr-atmosphere/tma-framework
 * License: https://github.com/eubr-atmosphere/tma-framework/blob/master/LICENSE
 * <p>
 * <p>
 */
package eu.atmosphere.tmaf.monitor.message;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.annotation.JsonValue;
import java.util.Arrays;

/**
 * tma-m_schema_0_3::Data
 * <p>
 * <p>
 * @author Nuno Antunes <nmsa@dei.uc.pt>
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "type",
    "descriptionId",
    "metricId",
    "observations"
})
public class Data implements Serializable {

    /**
     *
     * (Required)
     * <p>
     */
    @JsonProperty("type")
    private Data.Type type = Data.Type.fromValue("measurement");
    /**
     *
     * (Required)
     * <p>
     */
    @JsonProperty("descriptionId")
    private long descriptionId = -10L;
    /**
    *
    * (Required)
    * <p>
    */
    @JsonProperty("metricId")
    private long metricId = -10L;
    /**
     *
     * (Required)
     * <p>
     */
    @JsonProperty("observations")
    private List<Observation> observations = new ArrayList<Observation>();

    private final static long serialVersionUID = -2216070550858223535L;

    /**
     * No args constructor for use in serialization
     * <p>
     */
    public Data() {
    }

    /**
     *
     * @param descriptionId
     * @param type
     * @param observations
     */
    public Data(Data.Type type, long descriptionId, List<Observation> observations) {
        super();
        this.type = type;
        this.descriptionId = descriptionId;
        this.observations.addAll(observations);
    }

    public Data(Data.Type type, long descriptionId, Observation... observations) {
        this.type = type;
        this.descriptionId = descriptionId;
        this.observations.addAll(Arrays.asList(observations));
    }
    
    public Data(Data.Type type, long descriptionId, long metricId, Observation... observations) {
        this.type = type;
        this.descriptionId = descriptionId;
        this.metricId = metricId;
        this.observations.addAll(Arrays.asList(observations));
    }

    /**
     *
     * @return 
     */
    @JsonProperty("type")
    public Data.Type getType() {
        return type;
    }

    /**
     *
     */
    @JsonProperty("type")
    public void setType(Data.Type type) {
        this.type = type;
    }

    /**
     *
     */
    @JsonProperty("descriptionId")
    public long getDescriptionId() {
        return descriptionId;
    }

    /**
     *
     */
    @JsonProperty("descriptionId")
    public void setDescriptionId(long descriptionId) {
        this.descriptionId = descriptionId;
    }

    /**
    *
    */
    @JsonProperty("metricId")
    public long getMetricId() {
		return metricId;
	}

    /**
    *
    */
    @JsonProperty("metricId")
	public void setMetricId(long metricId) {
		this.metricId = metricId;
	}

	/**
     *
     */
    @JsonProperty("observations")
    public List<Observation> getObservations() {
        return observations;
    }

    /**
     *
     */
    @JsonProperty("observations")
    public void setObservations(List<Observation> observations) {
        this.observations = observations;
    }

    @Override
    public String toString() {
        return new StringBuilder("Datum{").append("type:").append(type).
                append(", descriptionId:").append(descriptionId).
                append(", observations:").append(observations).append("}").
                toString();
    }

    public enum Type {

        MEASUREMENT("measurement"),
        EVENT("event");
        private final String value;
        private final static Map<String, Data.Type> CONSTANTS = new HashMap<String, Data.Type>();

        static {
            for (Data.Type c : values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        private Type(String value) {
            this.value = value;
        }

        @Override
        public String toString() {
            return this.value;
        }

        @JsonValue
        public String value() {
            return this.value;
        }

        @JsonCreator
        public static Data.Type fromValue(String value) {
            Data.Type constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }
    }
}
